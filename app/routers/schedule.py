from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date as dt
from app.database import get_db
from app.models import User, Schedule
from app.schemas import ScheduleOut, GenerateScheduleRequest
from app.auth import get_current_user
from app.services import ai_service
from app.services.subscription import check_limit
import json

router = APIRouter(prefix="/schedule", tags=["Schedule"])

@router.get("/today", response_model=ScheduleOut | None)
def get_today(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = str(dt.today())
    return db.query(Schedule).filter(Schedule.user_id == user.id, Schedule.date == today).first()

@router.get("/history", response_model=list[ScheduleOut])
def get_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.services.subscription import get_limits
    days = get_limits(user.plan)["history_days"]
    schedules = (
        db.query(Schedule)
        .filter(Schedule.user_id == user.id)
        .order_by(Schedule.date.desc())
        .limit(days)
        .all()
    )
    return schedules

@router.post("/generate", response_model=ScheduleOut)
def generate(
    req:  GenerateScheduleRequest,
    user: User = Depends(get_current_user),
    db:   Session = Depends(get_db),
):
    target_date = req.date or str(dt.today())

    # Bugun nechta generatsiya qilingan
    today_count = db.query(Schedule).filter(
        Schedule.user_id == user.id,
        Schedule.date == target_date
    ).count()

    if not check_limit(user.plan, "ai_generate", today_count):
        raise HTTPException(status_code=403, detail="Bugungi generatsiya limitiga yetdingiz.")

    result = ai_service.generate_schedule(user, target_date, req.notes or "")

    schedule = db.query(Schedule).filter(
        Schedule.user_id == user.id, Schedule.date == target_date
    ).first()

    if schedule:
        schedule.content   = json.dumps(result.get("schedule", []), ensure_ascii=False)
        schedule.ai_advice = result.get("advice", "")
    else:
        schedule = Schedule(
            user_id   = user.id,
            date      = target_date,
            content   = json.dumps(result.get("schedule", []), ensure_ascii=False),
            ai_advice = result.get("advice", ""),
        )
        db.add(schedule)

    db.commit()
    db.refresh(schedule)
    return schedule
