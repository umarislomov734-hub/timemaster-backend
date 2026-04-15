from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Goal
from app.schemas import GoalCreate, GoalOut
from app.auth import get_current_user
from app.services.subscription import check_limit

router = APIRouter(prefix="/goals", tags=["Goals"])

@router.get("", response_model=list[GoalOut])
def list_goals(user: User = Depends(get_current_user)):
    return user.goals

@router.post("", response_model=GoalOut)
def create_goal(
    data: GoalCreate,
    user: User = Depends(get_current_user),
    db:   Session = Depends(get_db),
):
    active_count = sum(1 for g in user.goals if not g.is_done)
    if not check_limit(user.plan, "goals", active_count):
        raise HTTPException(status_code=403, detail=f"Tarifingizda maksimal maqsad limitiga yetdingiz. Pro yoki Premium ga o'ting.")

    goal = Goal(user_id=user.id, **data.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal

@router.patch("/{goal_id}/done", response_model=GoalOut)
def mark_done(
    goal_id: int,
    user: User = Depends(get_current_user),
    db:   Session = Depends(get_db),
):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Maqsad topilmadi")
    goal.is_done = True
    db.commit()
    db.refresh(goal)
    return goal

@router.delete("/{goal_id}")
def delete_goal(
    goal_id: int,
    user: User = Depends(get_current_user),
    db:   Session = Depends(get_db),
):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Maqsad topilmadi")
    db.delete(goal)
    db.commit()
    return {"ok": True}
