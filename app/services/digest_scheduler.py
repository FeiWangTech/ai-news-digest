import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from zoneinfo import ZoneInfo

from ..config import settings
from ..database import async_session_maker
from ..models.user import User
from ..models.preference import UserPreference
from ..models.digest import Digest, DigestItem, DigestStatus
from ..services.fetcher import fetch_all_sources
from ..services.email_service import send_digest_email, render_digest_html, build_items_html

logger = logging.getLogger("app.scheduler")


class DigestScheduler:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()

    def start(self) -> None:
        self.scheduler.add_job(
            self._process_digests,
            trigger=IntervalTrigger(minutes=30),
            id="digest_processor",
            replace_existing=True,
            max_instances=1,
        )
        self.scheduler.start()
        logger.info("Digest scheduler started")

    def shutdown(self) -> None:
        self.scheduler.shutdown(wait=False)
        logger.info("Digest scheduler stopped")

    async def _process_digests(self) -> None:
        """Find users whose email_time window has passed and process digests."""
        now_utc = datetime.now(timezone.utc)
        async with async_session_maker() as db:
            result = await db.execute(select(UserPreference).where(UserPreference.subscribed.is_(True)))
            prefs = result.scalars().all()

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

                window_start = (datetime.combine(datetime.today(), target_time) - timedelta(minutes=30)).time()
                window_end = (datetime.combine(datetime.today(), target_time) + timedelta(minutes=30)).time()

                in_window = window_start <= window_end and (window_start <= now_time <= window_end)
                wrapped = window_start > window_end and (now_time >= window_start or now_time <= window_end)

                if not (in_window or wrapped):
                    continue

                has_pending = await db.execute(
                    select(Digest).where(
                        Digest.user_id == user.id,
                        Digest.status == DigestStatus.pending.value,
                    )
                )
                if has_pending.scalar_one_or_none():
                    continue

                await self._generate_and_send(db, user, pref)

    async def _generate_and_send(self, db: AsyncSession, user: User, pref: UserPreference) -> None:
        """Generate a digest for a user and send it via email."""
        items = fetch_all_sources(user_id=user.id)
        if not items:
            logger.info("No items for user %s; skipping", user.id)
            return

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
        await db.flush()

        for idx, item in enumerate(items):
            db.add(
                DigestItem(
                    digest_id=digest.id,
                    source=item["source"],
                    title=item["title"],
                    url=item["url"],
                    score=item.get("score"),
                    position=idx + 1,
                )
            )

        await db.commit()
        await db.refresh(digest)

        sent = send_digest_email(to_email=user.email, subject=digest.subject, html_content=digest.html_content)
        digest.status = DigestStatus.sent.value if sent else DigestStatus.failed.value
        digest.sent_at = datetime.now(timezone.utc) if sent else None
        await db.commit()

        logger.info("Digest %s for user %s processed (status=%s)", digest.id, user.id, digest.status)


scheduler = DigestScheduler()
