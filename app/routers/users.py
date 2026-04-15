from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import ProfileUpdate, ProfileOut
from app.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "id":    user.id,
        "name":  user.name,
        "email": user.email,
        "plan":  user.plan.value,
    }

@router.get("/profile", response_model=ProfileOut)
def get_profile(user: User = Depends(get_current_user)):
    return user.profile

@router.put("/profile", response_model=ProfileOut)
def update_profile(
    data: ProfileUpdate,
    user: User = Depends(get_current_user),
    db:   Session = Depends(get_db),
):
    profile = user.profile
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile
