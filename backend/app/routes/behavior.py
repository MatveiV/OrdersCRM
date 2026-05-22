from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.behavior import (
    BehaviorCreate, BehaviorUpdate, BehaviorResponse, BehaviorCRUD
)
from app.models.admin_user import AdminUserModel

router = APIRouter(prefix="/behaviors", tags=["Behaviors"])


@router.post("/", response_model=BehaviorResponse, status_code=201)
async def create_behavior(behavior: BehaviorCreate, db: AsyncSession = Depends(get_db)):
    existing = await BehaviorCRUD.get(db, behavior.lead_id)
    if existing:
        raise HTTPException(status_code=400, detail="Behavior already exists for this lead")
    return await BehaviorCRUD.create(db, behavior)


@router.get("/", response_model=List[BehaviorResponse])
async def get_behaviors(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    return await BehaviorCRUD.get_all(db, skip, limit)


@router.get("/{lead_id}", response_model=BehaviorResponse)
async def get_behavior(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    behavior = await BehaviorCRUD.get(db, lead_id)
    if not behavior:
        raise HTTPException(status_code=404, detail="Behavior not found")
    return behavior


@router.put("/{lead_id}", response_model=BehaviorResponse)
async def update_behavior(
    lead_id: int,
    behavior: BehaviorUpdate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    updated = await BehaviorCRUD.update(db, lead_id, behavior)
    if not updated:
        raise HTTPException(status_code=404, detail="Behavior not found")
    return updated


@router.delete("/{lead_id}", status_code=204)
async def delete_behavior(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    deleted = await BehaviorCRUD.delete(db, lead_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Behavior not found")
    return None
