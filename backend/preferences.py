from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from dependencies import get_db, UserModel, JobPreferences
from users import get_current_user

router = APIRouter()

class JobPreferencesRequest(BaseModel):
    role: str
    location: str
    industry: str
    remote: Optional[bool] = False

@router.post("/preferences")
def save_preferences(preferences: JobPreferencesRequest, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    user_id = db.query(UserModel).filter(UserModel.username == current_user).first().id
    new_preferences = JobPreferences(
        user_id=user_id,
        role=preferences.role,
        location=preferences.location,
        industry=preferences.industry,
        remote=preferences.remote,
    )
    db.add(new_preferences)
    db.commit()
    db.refresh(new_preferences)
    return {"message": "Preferences saved successfully", "preferences": preferences}

@router.get("/preferences")
def get_preferences(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    user_id = db.query(UserModel).filter(UserModel.username == current_user).first().id
    preferences = db.query(JobPreferences).filter(JobPreferences.user_id == user_id).all()
    return preferences