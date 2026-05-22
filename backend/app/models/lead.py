from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy import delete as sqlalchemy_delete
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.core.database import Base


"""
CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    middle_name VARCHAR(255),
    contact_data TEXT,
    business_niche VARCHAR(255),
    company_size VARCHAR(100),
    task_volume VARCHAR(255),
    role VARCHAR(100),
    business_info TEXT,
    budget VARCHAR(100),
    project_deadline VARCHAR(255),
    task_type VARCHAR(255),
    product_interest VARCHAR(255),
    preferred_contact_method VARCHAR(100),
    convenient_time VARCHAR(100),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""


class LeadModel(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    middle_name = Column(String(255), nullable=True)
    contact_data = Column(Text, nullable=False)
    business_niche = Column(String(255), nullable=True)
    company_size = Column(String(100), nullable=True)
    task_volume = Column(String(255), nullable=True)
    role = Column(String(100), nullable=True)
    business_info = Column(Text, nullable=True)
    budget = Column(String(100), nullable=True)
    project_deadline = Column(String(255), nullable=True)
    task_type = Column(String(255), nullable=True)
    product_interest = Column(String(255), nullable=True)
    preferred_contact_method = Column(String(100), nullable=True)
    convenient_time = Column(String(100), nullable=True)
    comment = Column(Text, nullable=True)
    priority = Column(String(20), default="medium")
    status = Column(String(20), default="new")
    planned_start_date = Column(Text, nullable=True)
    planned_end_date = Column(Text, nullable=True)
    assigned_to = Column(String(255), nullable=True)
    estimated_cost = Column(Integer, nullable=True)
    actual_cost = Column(Integer, nullable=True)
    payment_status = Column(String(20), default="unpaid")
    created_at = Column(Text, default=lambda: datetime.now().isoformat())
    updated_at = Column(Text, default=lambda: datetime.now().isoformat(), onupdate=lambda: datetime.now().isoformat())


class LeadCreate(BaseModel):
    model_config = {"extra": "ignore"}
    
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    contact_data: str
    business_niche: Optional[str] = None
    company_size: Optional[str] = None
    task_volume: Optional[str] = None
    role: Optional[str] = None
    business_info: Optional[str] = None
    budget: Optional[str] = None
    project_deadline: Optional[str] = None
    task_type: Optional[str] = None
    product_interest: Optional[str] = None
    preferred_contact_method: Optional[str] = None
    convenient_time: Optional[str] = None
    comment: Optional[str] = None


class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    contact_data: Optional[str] = None
    business_niche: Optional[str] = None
    company_size: Optional[str] = None
    task_volume: Optional[str] = None
    role: Optional[str] = None
    business_info: Optional[str] = None
    budget: Optional[str] = None
    project_deadline: Optional[str] = None
    task_type: Optional[str] = None
    product_interest: Optional[str] = None
    preferred_contact_method: Optional[str] = None
    convenient_time: Optional[str] = None
    comment: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    planned_start_date: Optional[str] = None
    planned_end_date: Optional[str] = None
    assigned_to: Optional[str] = None
    estimated_cost: Optional[int] = None
    actual_cost: Optional[int] = None
    payment_status: Optional[str] = None


class LeadResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    contact_data: str
    business_niche: Optional[str] = None
    company_size: Optional[str] = None
    task_volume: Optional[str] = None
    role: Optional[str] = None
    business_info: Optional[str] = None
    budget: Optional[str] = None
    project_deadline: Optional[str] = None
    task_type: Optional[str] = None
    product_interest: Optional[str] = None
    preferred_contact_method: Optional[str] = None
    convenient_time: Optional[str] = None
    comment: Optional[str] = None
    priority: str = "medium"
    status: str = "new"
    planned_start_date: Optional[str] = None
    planned_end_date: Optional[str] = None
    assigned_to: Optional[str] = None
    estimated_cost: Optional[int] = None
    actual_cost: Optional[int] = None
    payment_status: str = "unpaid"
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class LeadCRUD:
    @staticmethod
    async def create(db: AsyncSession, lead: LeadCreate) -> LeadModel:
        db_lead = LeadModel(**lead.model_dump())
        db.add(db_lead)
        await db.commit()
        await db.refresh(db_lead)
        return db_lead

    @staticmethod
    async def get(db: AsyncSession, lead_id: int) -> Optional[LeadModel]:
        result = await db.execute(select(LeadModel).where(LeadModel.id == lead_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[LeadModel]:
        result = await db.execute(select(LeadModel).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def update(db: AsyncSession, lead_id: int, lead: LeadUpdate) -> Optional[LeadModel]:
        db_lead = await LeadCRUD.get(db, lead_id)
        if not db_lead:
            return None
        update_data = lead.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_lead, key, value)
        await db.commit()
        await db.refresh(db_lead)
        return db_lead

    @staticmethod
    async def delete(db: AsyncSession, lead_id: int) -> bool:
        db_lead = await LeadCRUD.get(db, lead_id)
        if not db_lead:
            return False
        await db.delete(db_lead)
        await db.commit()
        return True
