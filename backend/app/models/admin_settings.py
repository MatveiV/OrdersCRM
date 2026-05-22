from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from datetime import datetime

from app.core.database import Base


"""
CREATE TABLE admin_settings (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    budget_range TEXT,
    task_type VARCHAR(255),
    product_interest VARCHAR(255),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_admin_settings_service_name ON admin_settings(service_name);
"""


class AdminSettingModel(Base):
    __tablename__ = "admin_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_name = Column(String(255), nullable=False)
    budget_range = Column(Text, nullable=True)
    task_type = Column(String(255), nullable=True)
    product_interest = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(Text, default=lambda: datetime.now().isoformat())
    updated_at = Column(Text, default=lambda: datetime.now().isoformat(), onupdate=lambda: datetime.now().isoformat())


class AdminSettingCRUD:
    @staticmethod
    async def get_all(db: AsyncSession) -> List[AdminSettingModel]:
        result = await db.execute(select(AdminSettingModel).order_by(AdminSettingModel.id))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, setting_id: int) -> Optional[AdminSettingModel]:
        result = await db.execute(select(AdminSettingModel).where(AdminSettingModel.id == setting_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: dict) -> AdminSettingModel:
        setting = AdminSettingModel(**data)
        db.add(setting)
        await db.commit()
        await db.refresh(setting)
        return setting

    @staticmethod
    async def update(db: AsyncSession, setting_id: int, data: dict) -> Optional[AdminSettingModel]:
        setting = await AdminSettingCRUD.get_by_id(db, setting_id)
        if not setting:
            return None
        for key, value in data.items():
            setattr(setting, key, value)
        await db.commit()
        await db.refresh(setting)
        return setting

    @staticmethod
    async def delete(db: AsyncSession, setting_id: int) -> bool:
        setting = await AdminSettingCRUD.get_by_id(db, setting_id)
        if not setting:
            return False
        await db.delete(setting)
        await db.commit()
        return True
