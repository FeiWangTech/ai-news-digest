import json
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, UserPreference, DigestHistory
from schemas import DigestOut
from routers.auth import current_user
from services.email_service import send_email
from services.news_fetcher import fetch_hackernews_ai, fetch_techcrunch_ai, fetch_arxiv_ai, build_email_html
from apscheduler.schedulers.background import BackgroundScheduler

router = APIRouter(prefix="/digests", tags=["digests"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

scheduler = BackgroundScheduler()
scheduler.start()

def generate_send(user_id: int):
    from database import SessionLocal
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return
        pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
        sources = json.loads(pref.sources or "[]") if pref else ["hackernews","techcrunch","arxiv"]
        topics = json.loads(pref.topics or "[]") if pref else []
        query = " ".join(topics) if topics else "AI OR LLM"
        hn_items = fetch_hackernews_ai(query=query, limit=10) if "hackernews" in sources else []
        tc_items = fetch_techcrunch_ai(limit=10) if "techcrunch" in sources else []
        arxiv_items = fetch_arxiv_ai(limit=10) if "arxiv" in sources else []
        html = build_email_html(hn_items, tc_items, arxiv_items)
        subject = f"🤖 AI Daily Digest — {datetime.now().strftime('%b %d, %Y')}"
        if send_email(user.email, subject, html):
            hist = DigestHistory(user_id=user.id, subject=subject, body_html=html)
            db.add(hist)
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Scheduled digest error for user {user_id}: {e}")
    finally:
        db.close()

@router.post("/send-now", response_model=DigestOut)
def send_now(email: str = Depends(current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    generate_send(user.id)
    return db.query(DigestHistory).filter(DigestHistory.user_id == user.id).order_by(DigestHistory.sent_at.desc()).first()

@router.get("/history", response_model=list[DigestOut])
def history(email: str = Depends(current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return db.query(DigestHistory).filter(DigestHistory.user_id == user.id).order_by(DigestHistory.sent_at.desc()).all()

def schedule_user(pref: UserPreference):
    job_id = f"digest_{pref.user_id}"
    try:
        scheduler.remove_job(job_id)
    except Exception:
        pass
    if pref.frequency == "weekly":
        trigger = "cron"
        kwargs = {"day_of_week": "mon", "hour": int(pref.send_time.split(":")[0]), "minute": int(pref.send_time.split(":")[1])}
    else:
        trigger = "cron"
        kwargs = {"hour": int(pref.send_time.split(":")[0]), "minute": int(pref.send_time.split(":")[1])}
    from datetime import timezone
    scheduler.add_job(generate_send, trigger=trigger, args=[pref.user_id], id=job_id, **kwargs)
