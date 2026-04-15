from fastapi import APIRouter, Depends, HTTPException
from app.models import User
from app.schemas import AIAdviceRequest, AIAdviceResponse
from app.auth import get_current_user
from app.services import ai_service
from app.services.subscription import check_limit

router = APIRouter(prefix="/ai", tags=["AI"])

# Oddiy in-memory counter (production da Redis ishlatiladi)
_advice_counter: dict[int, int] = {}

@router.post("/advice", response_model=AIAdviceResponse)
def get_advice(
    req:  AIAdviceRequest,
    user: User = Depends(get_current_user),
):
    count = _advice_counter.get(user.id, 0)
    if not check_limit(user.plan, "ai_advice", count):
        raise HTTPException(status_code=403, detail="Maslahat limitiga yetdingiz. Tarifni yangilang.")

    _advice_counter[user.id] = count + 1
    advice = ai_service.get_advice(user, req.message)
    return AIAdviceResponse(advice=advice)
