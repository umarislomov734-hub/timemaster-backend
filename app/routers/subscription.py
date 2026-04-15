from fastapi import APIRouter, Depends
from app.models import User
from app.schemas import SubscriptionStatus
from app.auth import get_current_user
from app.services.subscription import get_limits

router = APIRouter(prefix="/subscription", tags=["Subscription"])

PLAN_PRICES = {"trial": 0, "starter": 5, "pro": 10, "premium": 15}

@router.get("/status", response_model=SubscriptionStatus)
def status(user: User = Depends(get_current_user)):
    limits = get_limits(user.plan)
    return SubscriptionStatus(
        plan       = user.plan.value,
        is_active  = user.is_active,
        trial_ends = user.trial_ends,
        limits     = limits,
    )

@router.get("/plans")
def plans():
    return [
        {
            "id":       "starter",
            "name":     "Starter",
            "price":    5,
            "currency": "USD",
            "features": [
                "3 ta maqsad",
                "Kunlik AI jadval (1x)",
                "3 ta AI maslahat/kun",
                "7 kunlik tarix",
            ]
        },
        {
            "id":       "pro",
            "name":     "Pro",
            "price":    10,
            "currency": "USD",
            "features": [
                "10 ta maqsad",
                "Kunlik AI jadval (3x)",
                "20 ta AI maslahat/kun",
                "30 kunlik tarix",
                "Haftalik tahlil",
            ]
        },
        {
            "id":       "premium",
            "name":     "Premium",
            "price":    15,
            "currency": "USD",
            "features": [
                "Cheksiz maqsadlar",
                "Cheksiz AI jadval",
                "Cheksiz AI maslahat",
                "1 yillik tarix",
                "AI coach",
                "Ustuvor yordam",
            ]
        },
    ]
