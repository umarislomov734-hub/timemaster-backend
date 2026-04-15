from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ── Auth ─────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    plan: str
    name: str

# ── Profile ───────────────────────────────────────────────────────────
class ProfileUpdate(BaseModel):
    wake_time:  Optional[str] = None
    sleep_time: Optional[str] = None
    work_start: Optional[str] = None
    work_end:   Optional[str] = None
    work_days:  Optional[str] = None
    occupation: Optional[str] = None
    priorities: Optional[str] = None
    language:   Optional[str] = None

class ProfileOut(BaseModel):
    wake_time:  str
    sleep_time: str
    work_start: str
    work_end:   str
    work_days:  str
    occupation: Optional[str]
    priorities: Optional[str]
    language:   str

    class Config:
        from_attributes = True

# ── Goals ─────────────────────────────────────────────────────────────
class GoalCreate(BaseModel):
    title:    str
    category: str
    deadline: Optional[datetime] = None

class GoalOut(BaseModel):
    id:       int
    title:    str
    category: str
    is_done:  bool
    deadline: Optional[datetime]

    class Config:
        from_attributes = True

# ── Schedule ──────────────────────────────────────────────────────────
class ScheduleOut(BaseModel):
    date:      str
    content:   str
    ai_advice: Optional[str]

    class Config:
        from_attributes = True

# ── AI ────────────────────────────────────────────────────────────────
class AIAdviceRequest(BaseModel):
    message: str   # foydalanuvchi muammosi

class AIAdviceResponse(BaseModel):
    advice: str

class GenerateScheduleRequest(BaseModel):
    date:  Optional[str] = None   # YYYY-MM-DD, default bugun
    notes: Optional[str] = None   # qo'shimcha eslatmalar

# ── Subscription ─────────────────────────────────────────────────────
class SubscriptionStatus(BaseModel):
    plan:        str
    is_active:   bool
    trial_ends:  Optional[datetime]
    limits:      dict
