from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.admin_user import AdminUserModel
from app.models.behavior_metric import (
    BehaviorMetricCreate, BehaviorMetricResponse, BehaviorMetricCRUD
)

router = APIRouter(prefix="/behavior-metrics", tags=["Behavior Metrics"])


@router.post("/", response_model=BehaviorMetricResponse, status_code=201)
async def create_behavior_metric(
    data: BehaviorMetricCreate,
    db: AsyncSession = Depends(get_db),
):
    return await BehaviorMetricCRUD.create(db, data)


@router.get("/", response_model=List[BehaviorMetricResponse])
async def get_behavior_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    return await BehaviorMetricCRUD.get_all(db, skip, limit)


@router.get("/stats")
async def get_behavior_metrics_stats(
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    return await BehaviorMetricCRUD.get_stats(db)
