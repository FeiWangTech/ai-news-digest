from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from database import get_db
from models import User, UserPreference
from schemas import PreferenceUpdate, PreferenceResponse
from auth import get_current_user

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("/", response_model=PreferenceResponse)
def get_preference(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preference not found")
    return pref


@router.put("/", response_model=PreferenceResponse)
def update_preference(payload: PreferenceUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.add(pref)

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(pref, field, value)

    db.commit()
    db.refresh(pref)
    return pref
