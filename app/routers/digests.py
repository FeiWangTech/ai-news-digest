from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json

from database import get_db
from models import User, Digest, DigestItem
from schemas import DigestResponse, DigestListResponse, DigestListItem
from auth import get_current_user
from services.email_service import send_digest_email
from services.fetcher import fetch_all_sources
from services.scheduler import build_items_html, render_digest_html
from datetime import datetime

router = APIRouter(prefix="/digests", tags=["digests"])


@router.get("", response_model=DigestListResponse)
def list_digests(limit: int = 20, offset: int = 0, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total = db.query(Digest).filter(Digest.user_id == current_user.id).count()
    items = db.query(Digest).filter(Digest.user_id == current_user.id).order_by(Digest.created_at.desc()).limit(limit).offset(offset).all()
    return DigestListResponse(items=[DigestListItem.model_validate(i) for i in items], total=total)


@router.get("/{digest_id}", response_model=DigestResponse)
def get_digest(digest_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    digest = db.query(Digest).filter(Digest.id == digest_id, Digest.user_id == current_user.id).first()
    if not digest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Digest not found")
    return digest


@router.post("/generate", response_model=dict)
def generate_digest(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pending = db.query(Digest).filter(Digest.user_id == current_user.id, Digest.status == "pending").first()
    if pending:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A pending digest already exists")

    items = fetch_all_sources(user_id=current_user.id)
    if not items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No items available right now")

    items_html = build_items_html(items)
    html_content = render_digest_html(
        subject="Your On-Demand AI Digest",
        greeting=f"Hello {current_user.email}, here is your on-demand update.",
        items_html=items_html,
    )

    digest = Digest(
        user_id=current_user.id,
        subject="Your On-Demand AI Digest",
        html_content=html_content,
        status="pending",
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

    sent = send_digest_email(to_email=current_user.email, subject=digest.subject, html_content=digest.html_content)
    digest.status = "sent" if sent else "failed"
    digest.sent_at = datetime.now(timezone.utc) if sent else None
    db.commit()

    return {"detail": "Digest generated", "status": digest.status, "digest_id": digest.id}
