from sqlalchemy import Column, Integer, String, Text, JSON, Boolean
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.core.database import Base


"""
CREATE TABLE admin_data (
    id SERIAL PRIMARY KEY,
    service_name TEXT,
    budget_range TEXT,
    available_products TEXT,
    contact_methods TEXT,
    form_settings JSON,
    ui_config JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""


class AdminDataModel(Base):
    __tablename__ = "admin_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_name = Column(Text, nullable=True)
    budget_range = Column(Text, nullable=True)
    available_products = Column(Text, nullable=True)
    contact_methods = Column(Text, nullable=True)
    form_settings = Column(JSON, nullable=True)
    ui_config = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(Text, default=lambda: datetime.now().isoformat())
    updated_at = Column(Text, default=lambda: datetime.now().isoformat(), onupdate=lambda: datetime.now().isoformat())


class AdminDataCreate(BaseModel):
    service_name: Optional[str] = None
    budget_range: Optional[str] = None
    available_products: Optional[str] = None
    contact_methods: Optional[str] = None
    form_settings: Optional[dict] = None
    ui_config: Optional[dict] = None
    is_active: Optional[bool] = True


class AdminDataUpdate(BaseModel):
    service_name: Optional[str] = None
    budget_range: Optional[str] = None
    available_products: Optional[str] = None
    contact_methods: Optional[str] = None
    form_settings: Optional[dict] = None
    ui_config: Optional[dict] = None
    is_active: Optional[bool] = None


class AdminDataResponse(BaseModel):
    id: int
    service_name: Optional[str] = None
    budget_range: Optional[str] = None
    available_products: Optional[str] = None
    contact_methods: Optional[str] = None
    form_settings: Optional[dict] = None
    ui_config: Optional[dict] = None
    is_active: bool = True
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class AdminDataCRUD:
    @staticmethod
    async def create(db: AsyncSession, data: AdminDataCreate) -> AdminDataModel:
        db_data = AdminDataModel(**data.model_dump())
        db.add(db_data)
        await db.commit()
        await db.refresh(db_data)
        return db_data

    @staticmethod
    async def get(db: AsyncSession, data_id: int) -> Optional[AdminDataModel]:
        result = await db.execute(select(AdminDataModel).where(AdminDataModel.id == data_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[AdminDataModel]:
        result = await db.execute(select(AdminDataModel).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_active(db: AsyncSession) -> Optional[AdminDataModel]:
        result = await db.execute(select(AdminDataModel).where(AdminDataModel.is_active == True).limit(1))
        return result.scalar_one_or_none()

    @staticmethod
    async def update(db: AsyncSession, data_id: int, data: AdminDataUpdate) -> Optional[AdminDataModel]:
        db_data = await AdminDataCRUD.get(db, data_id)
        if not db_data:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_data, key, value)
        await db.commit()
        await db.refresh(db_data)
        return db_data

    @staticmethod
    async def delete(db: AsyncSession, data_id: int) -> bool:
        db_data = await AdminDataCRUD.get(db, data_id)
        if not db_data:
            return False
        await db.delete(db_data)
        await db.commit()
        return True
