from sqlalchemy import Column, Integer, String, Text, JSON, Float, ForeignKey
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.core.database import Base


"""
CREATE TABLE behaviors (
    lead_id INTEGER PRIMARY KEY REFERENCES leads(id) ON DELETE CASCADE,
    time_spent_seconds FLOAT,
    buttons_clicked TEXT,
    cursor_hover_zones TEXT,
    return_count INTEGER DEFAULT 0,
    page_views INTEGER DEFAULT 0,
    scroll_depth_percent FLOAT,
    device_type VARCHAR(50),
    browser VARCHAR(100),
    os VARCHAR(100),
    screen_resolution VARCHAR(20),
    ip_address VARCHAR(45),
    user_agent TEXT,
    referrer VARCHAR(500),
    utm_source VARCHAR(255),
    utm_medium VARCHAR(255),
    utm_campaign VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""


class BehaviorModel(Base):
    __tablename__ = "behaviors"

    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), primary_key=True)
    time_spent_seconds = Column(Float, nullable=True)
    buttons_clicked = Column(Text, nullable=True)
    cursor_hover_zones = Column(Text, nullable=True)
    return_count = Column(Integer, default=0)
    page_views = Column(Integer, default=0)
    scroll_depth_percent = Column(Float, nullable=True)
    device_type = Column(String(50), nullable=True)
    browser = Column(String(100), nullable=True)
    os = Column(String(100), nullable=True)
    screen_resolution = Column(String(20), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    referrer = Column(String(500), nullable=True)
    utm_source = Column(String(255), nullable=True)
    utm_medium = Column(String(255), nullable=True)
    utm_campaign = Column(String(255), nullable=True)
    created_at = Column(Text, default=lambda: datetime.now().isoformat())
    updated_at = Column(Text, default=lambda: datetime.now().isoformat(), onupdate=lambda: datetime.now().isoformat())


class BehaviorCreate(BaseModel):
    lead_id: int
    time_spent_seconds: Optional[float] = None
    buttons_clicked: Optional[str] = None
    cursor_hover_zones: Optional[str] = None
    return_count: Optional[int] = 0
    page_views: Optional[int] = 0
    scroll_depth_percent: Optional[float] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    screen_resolution: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None


class BehaviorUpdate(BaseModel):
    time_spent_seconds: Optional[float] = None
    buttons_clicked: Optional[str] = None
    cursor_hover_zones: Optional[str] = None
    return_count: Optional[int] = None
    page_views: Optional[int] = None
    scroll_depth_percent: Optional[float] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    screen_resolution: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None


class BehaviorResponse(BaseModel):
    lead_id: int
    time_spent_seconds: Optional[float] = None
    buttons_clicked: Optional[str] = None
    cursor_hover_zones: Optional[str] = None
    return_count: int = 0
    page_views: int = 0
    scroll_depth_percent: Optional[float] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    screen_resolution: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class BehaviorCRUD:
    @staticmethod
    async def create(db: AsyncSession, behavior: BehaviorCreate) -> BehaviorModel:
        db_behavior = BehaviorModel(**behavior.model_dump())
        db.add(db_behavior)
        await db.commit()
        await db.refresh(db_behavior)
        return db_behavior

    @staticmethod
    async def get(db: AsyncSession, lead_id: int) -> Optional[BehaviorModel]:
        result = await db.execute(select(BehaviorModel).where(BehaviorModel.lead_id == lead_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[BehaviorModel]:
        result = await db.execute(select(BehaviorModel).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def update(db: AsyncSession, lead_id: int, behavior: BehaviorUpdate) -> Optional[BehaviorModel]:
        db_behavior = await BehaviorCRUD.get(db, lead_id)
        if not db_behavior:
            return None
        update_data = behavior.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_behavior, key, value)
        await db.commit()
        await db.refresh(db_behavior)
        return db_behavior

    @staticmethod
    async def delete(db: AsyncSession, lead_id: int) -> bool:
        db_behavior = await BehaviorCRUD.get(db, lead_id)
        if not db_behavior:
            return False
        await db.delete(db_behavior)
        await db.commit()
        return True
