import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from config import settings
from database import SessionLocal
from models import User, UserPreference, Digest, DigestItem, DigestStatus
from services.fetcher import fetch_all_sources
from services.email_service import send_digest_email, render_digest_html, build_items_html

logger = logging.getLogger("app.scheduler")


def process_digests():
    now_utc = datetime.now(timezone.utc)
    db = SessionLocal()
    try:
        prefs = db.query(UserPreference).filter(UserPreference.subscribed.is_(True)).all()
        for pref in prefs:
            user = pref.user
            if not user or not user.is_active:
                continue

            tz = ZoneInfo(pref.timezone)
            now_local = now_utc.astimezone(tz)
            now_time = now_local.time()
            target_time = pref.email_time

            if target_time is None:
                continue

            from datetime import datetime as dt_datetime
            window_start = (dt_datetime.combine(dt_datetime.today(), target_time) - timedelta(minutes=30)).time()
            window_end = (dt_datetime.combine(dt_datetime.today(), target_time) + timedelta(minutes=30)).time()

            in_window = window_start <= window_end and (window_start <= now_time <= window_end)
            wrapped = window_start > window_end and (now_time >= window_start or now_time <= window_end)

            if not (in_window or wrapped):
                continue

            has_pending = db.query(Digest).filter(Digest.user_id == user.id, Digest.status == DigestStatus.pending.value).first()
            if has_pending:
                continue

            items = fetch_all_sources(user_id=user.id)
            if not items:
                logger.info("No items for user %s; skipping", user.id)
                continue

            items_html = build_items_html(items)
            html_content = render_digest_html(
                subject="Your AI Daily Digest",
                greeting=f"Hello {user.email}, here is your update.",
                items_html=items_html,
            )

            digest = Digest(
                user_id=user.id,
                user_preference_id=pref.id,
                subject="Your AI Daily Digest",
                html_content=html_content,
                status=DigestStatus.pending.value,
            )
            db.add(digest)
            db.commit()
            db.refresh(digest)

            for idx, item in enumerate(items):
                db.add(DigestItem(
                    digest_id=digest.id,
                    source=item.get("source", ""),
                    title=item["title"],
                    url=item["url"],
                    score=item.get("score"),
                    position=idx + 1,
                ))
            db.commit()

            sent = send_digest_email(to_email=user.email, subject=digest.subject, html_content=digest.html_content)
            digest.status = DigestStatus.sent.value if sent else DigestStatus.failed.value
            digest.sent_at = datetime.now(timezone.utc) if sent else None
            db.commit()

            logger.info("Digest %s for user %s processed (status=%s)", digest.id, user.id, digest.status)
    except Exception as exc:
        db.rollback()
        logger.exception("Scheduler error: %s", exc)
    finally:
        db.close()
