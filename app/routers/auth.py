from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.models import User, Profile, PlanType
from app.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.auth import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=TokenResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email allaqachon ro'yxatdan o'tgan")

    user = User(
        name       = data.name,
        email      = data.email,
        password   = hash_password(data.password),
        plan       = PlanType.trial,
        trial_ends = datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(user)
    db.flush()

    profile = Profile(user_id=user.id)
    db.add(profile)
    db.commit()

    return TokenResponse(
        access_token=create_token(user.id),
        plan=user.plan.value,
        name=user.name,
    )

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Email yoki parol noto'g'ri")

    return TokenResponse(
        access_token=create_token(user.id),
        plan=user.plan.value,
        name=user.name,
    )
