from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.core.database import Base


class BehaviorMetricModel(Base):
    __tablename__ = "behavior_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(Integer, default=0)
    time_on_page = Column(Integer, default=0)
    buttons_clicked = Column(Text, nullable=True)
    cursor_positions = Column(Text, nullable=True)
    return_frequency = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BehaviorMetricCreate(BaseModel):
    application_id: Optional[int] = 0
    time_on_page: Optional[int] = 0
    buttons_clicked: Optional[str] = None
    cursor_positions: Optional[str] = None
    return_frequency: Optional[int] = 0


class BehaviorMetricResponse(BaseModel):
    id: int
    application_id: int
    time_on_page: int
    buttons_clicked: Optional[str] = None
    cursor_positions: Optional[str] = None
    return_frequency: int
    created_at: datetime

    class Config:
        from_attributes = True


class BehaviorMetricCRUD:
    @staticmethod
    async def create(db: AsyncSession, data: BehaviorMetricCreate) -> BehaviorMetricModel:
        record = BehaviorMetricModel(**data.model_dump())
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[BehaviorMetricModel]:
        result = await db.execute(
            select(BehaviorMetricModel).order_by(BehaviorMetricModel.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_stats(db: AsyncSession) -> dict:
        now = datetime.now()

        # Daily stats: last 1 day
        daily_result = await db.execute(text("""
            SELECT
                COALESCE(AVG(sub.max_time), 0) as avg_time,
                COALESCE(MAX(sub.max_time), 0) as max_time
            FROM (
                SELECT MAX(time_on_page) as max_time
                FROM behavior_metrics
                WHERE created_at >= :daily_cutoff
                GROUP BY DATE(created_at)
            ) sub
        """), {"daily_cutoff": now.replace(hour=0, minute=0, second=0, microsecond=0)})
        daily_row = daily_result.fetchone()
        daily_avg = daily_row[0] if daily_row else 0
        daily_max = daily_row[1] if daily_row else 0

        # Weekly stats: last 7 days
        from datetime import timedelta
        week_ago = now - timedelta(days=7)
        weekly_result = await db.execute(text("""
            SELECT
                COALESCE(AVG(sub.max_time), 0) as avg_time,
                COALESCE(MAX(sub.max_time), 0) as max_time
            FROM (
                SELECT MAX(time_on_page) as max_time
                FROM behavior_metrics
                WHERE created_at >= :weekly_cutoff
                GROUP BY DATE(created_at)
            ) sub
        """), {"weekly_cutoff": week_ago})
        weekly_row = weekly_result.fetchone()
        weekly_avg = weekly_row[0] if weekly_row else 0
        weekly_max = weekly_row[1] if weekly_row else 0

        # Monthly stats: last 30 days
        month_ago = now - timedelta(days=30)
        monthly_result = await db.execute(text("""
            SELECT
                COALESCE(AVG(sub.max_time), 0) as avg_time,
                COALESCE(MAX(sub.max_time), 0) as max_time
            FROM (
                SELECT MAX(time_on_page) as max_time
                FROM behavior_metrics
                WHERE created_at >= :monthly_cutoff
                GROUP BY DATE(created_at)
            ) sub
        """), {"monthly_cutoff": month_ago})
        monthly_row = monthly_result.fetchone()
        monthly_avg = monthly_row[0] if monthly_row else 0
        monthly_max = monthly_row[1] if monthly_row else 0

        # Top buttons: aggregate all buttons_clicked JSON strings
        buttons_result = await db.execute(text("""
            SELECT buttons_clicked FROM behavior_metrics
            WHERE buttons_clicked IS NOT NULL AND buttons_clicked != ''
            ORDER BY created_at DESC
            LIMIT 1000
        """))
        button_aggr = {}
        for row in buttons_result.fetchall():
            raw = row[0]
            if not raw:
                continue
            try:
                import json
                data = json.loads(raw)
                if isinstance(data, dict):
                    for key, val in data.items():
                        button_aggr[key] = button_aggr.get(key, 0) + int(val)
            except (json.JSONDecodeError, ValueError, TypeError):
                pass
        top_buttons = sorted(button_aggr.items(), key=lambda x: -x[1])[:10]
        top_buttons_list = [{"button": k, "clicks": v} for k, v in top_buttons]

        # Heatmap data: aggregate cursor positions
        heatmap_result = await db.execute(text("""
            SELECT cursor_positions FROM behavior_metrics
            WHERE cursor_positions IS NOT NULL AND cursor_positions != ''
            ORDER BY created_at DESC
            LIMIT 500
        """))
        grid = {}
        for row in heatmap_result.fetchall():
            raw = row[0]
            if not raw:
                continue
            try:
                import json
                positions = json.loads(raw)
                if isinstance(positions, list):
                    for pos in positions:
                        if isinstance(pos, dict) and "x" in pos and "y" in pos:
                            gx = round(pos["x"] / 20) * 20
                            gy = round(pos["y"] / 20) * 20
                            key = (gx, gy)
                            grid[key] = grid.get(key, 0) + 1
            except (json.JSONDecodeError, ValueError, TypeError):
                pass
        heatmap_data = [{"x": int(k[0]), "y": int(k[1]), "frequency": v} for k, v in grid.items()]

        # Totals
        total_result = await db.execute(text("""
            SELECT COUNT(*) FROM behavior_metrics
        """))
        total_metrics = total_result.scalar() or 0

        total_sessions_result = await db.execute(text("""
            SELECT COUNT(DISTINCT DATE(created_at)) FROM behavior_metrics
        """))
        total_sessions = total_sessions_result.scalar() or 0

        return {
            "avg_time_on_page": {
                "daily": int(daily_avg),
                "weekly": int(weekly_avg),
                "monthly": int(monthly_avg),
            },
            "max_time_on_page": {
                "daily": int(daily_max),
                "weekly": int(weekly_max),
                "monthly": int(monthly_max),
            },
            "top_buttons": top_buttons_list,
            "heatmap_data": heatmap_data,
            "total_sessions": total_sessions,
            "total_metrics_records": total_metrics,
        }
