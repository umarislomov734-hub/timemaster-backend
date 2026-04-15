from app.models import PlanType

PLAN_LIMITS = {
    PlanType.trial: {
        "goals":         3,
        "ai_generate":   3,    # kunlik jadval generatsiya
        "ai_advice":     5,    # maslahat so'rash
        "history_days":  3,
        "price":         0,
    },
    PlanType.starter: {
        "goals":         3,
        "ai_generate":   1,
        "ai_advice":     3,
        "history_days":  7,
        "price":         5,
    },
    PlanType.pro: {
        "goals":         10,
        "ai_generate":   3,
        "ai_advice":     20,
        "history_days":  30,
        "price":         10,
    },
    PlanType.premium: {
        "goals":         999,
        "ai_generate":   10,
        "ai_advice":     999,
        "history_days":  365,
        "price":         15,
    },
}

def get_limits(plan: PlanType) -> dict:
    return PLAN_LIMITS.get(plan, PLAN_LIMITS[PlanType.trial])

def check_limit(plan: PlanType, feature: str, current_count: int) -> bool:
    limit = get_limits(plan).get(feature, 0)
    if limit == 999:
        return True
    return current_count < limit
