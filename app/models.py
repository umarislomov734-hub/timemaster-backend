from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
import enum

class PlanType(str, enum.Enum):
    starter  = "starter"   # $5
    pro      = "pro"       # $10
    premium  = "premium"   # $15
    trial    = "trial"     # 7 kun bepul

class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True)
    name       = Column(String(100))
    email      = Column(String(150), unique=True, index=True)
    password   = Column(String(200))
    plan       = Column(Enum(PlanType), default=PlanType.trial)
    trial_ends = Column(DateTime, nullable=True)
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    profile   = relationship("Profile",  back_populates="user", uselist=False, cascade="all, delete")
    goals     = relationship("Goal",     back_populates="user", cascade="all, delete")
    schedules = relationship("Schedule", back_populates="user", cascade="all, delete")


class Profile(Base):
    __tablename__ = "profiles"

    id           = Column(Integer, primary_key=True)
    user_id      = Column(Integer, ForeignKey("users.id"), unique=True)
    wake_time    = Column(String(5), default="07:00")   # HH:MM
    sleep_time   = Column(String(5), default="23:00")
    work_start   = Column(String(5), default="09:00")
    work_end     = Column(String(5), default="18:00")
    work_days    = Column(String(20), default="1,2,3,4,5")  # 1=Du, 7=Ya
    occupation   = Column(String(100), nullable=True)        # kasb
    priorities   = Column(Text, nullable=True)               # asosiy maqsadlar (json)
    language     = Column(String(5), default="uz")           # uz | ru | en

    user = relationship("User", back_populates="profile")


class Goal(Base):
    __tablename__ = "goals"

    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    title      = Column(String(200))
    category   = Column(String(50))  # ish, salomatlik, oila, o'rganish
    deadline   = Column(DateTime, nullable=True)
    is_done    = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="goals")


class Schedule(Base):
    __tablename__ = "schedules"

    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    date       = Column(String(10))   # YYYY-MM-DD
    content    = Column(Text)         # JSON — [{time, task, duration, category}]
    ai_advice  = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="schedules")
