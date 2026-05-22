from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.core.database import Base


class ApplicationModel(Base):
    __tablename__ = "applications"

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
    status = Column(String(50), default="Новая")
    notes = Column(Text, nullable=True, default="")
    created_at = Column(Text, default=lambda: datetime.now().isoformat())


class ApplicationCreate(BaseModel):
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
    status: Optional[str] = "Новая"
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
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
    status: Optional[str] = None
    notes: Optional[str] = None


class ApplicationResponse(BaseModel):
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
    status: str = "Новая"
    notes: Optional[str] = None
    created_at: str = ""
    scoring: Optional[dict] = None

    class Config:
        from_attributes = True


class ApplicationStatsResponse(BaseModel):
    total: int
    hot_count: int
    warm_count: int
    cold_count: int
    departments: list
    average_budget_max: float
    average_deadline_weeks: float
    personal_manager_rate: float


class ApplicationCRUD:
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ApplicationModel]:
        result = await db.execute(
            select(ApplicationModel).order_by(ApplicationModel.id.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, app_id: int) -> Optional[ApplicationModel]:
        result = await db.execute(select(ApplicationModel).where(ApplicationModel.id == app_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: ApplicationCreate) -> ApplicationModel:
        record = ApplicationModel(**data.model_dump())
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    @staticmethod
    async def update(db: AsyncSession, app_id: int, data: ApplicationUpdate) -> Optional[ApplicationModel]:
        record = await ApplicationCRUD.get_by_id(db, app_id)
        if not record:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(record, key, value)
        await db.commit()
        await db.refresh(record)
        return record

    @staticmethod
    async def get_stats(db: AsyncSession) -> dict:
        from app.core.scoring import calculate_lead_score

        result = await db.execute(select(ApplicationModel).order_by(ApplicationModel.id))
        apps = result.scalars().all()

        total = len(apps)
        hot = warm = cold = 0
        departments = {}
        total_budget_max = 0
        total_deadline_weeks = 0
        deadline_count = 0
        pm_count = 0

        for app in apps:
            app_dict = {c.name: getattr(app, c.name) for c in app.__table__.columns}
            scoring = calculate_lead_score(app_dict)
            if scoring["score"] >= 70:
                hot += 1
            elif scoring["score"] >= 40:
                warm += 1
            else:
                cold += 1
            dept = scoring["recommended_department"]
            departments[dept] = departments.get(dept, 0) + 1
            if scoring["needs_personal_manager"]:
                pm_count += 1

            from app.core.scoring import parse_budget
            bv = parse_budget(app_dict.get("budget") or "")
            if bv:
                total_budget_max += bv

            from app.core.scoring import parse_deadline_weeks
            dw = parse_deadline_weeks(app_dict.get("project_deadline") or "")
            if dw and dw < 99:
                total_deadline_weeks += dw
                deadline_count += 1

        return {
            "total": total,
            "hot_count": hot,
            "warm_count": warm,
            "cold_count": cold,
            "departments": [{"name": k, "count": v} for k, v in sorted(departments.items(), key=lambda x: -x[1])],
            "average_budget_max": round(total_budget_max / total, 2) if total else 0,
            "average_deadline_weeks": round(total_deadline_weeks / deadline_count, 2) if deadline_count else 0,
            "personal_manager_rate": round(pm_count / total * 100, 1) if total else 0,
        }
