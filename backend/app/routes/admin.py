from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.admin import (
    AdminDataCreate, AdminDataUpdate, AdminDataResponse, AdminDataCRUD
)
from app.models.admin_user import AdminUserModel

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/", response_model=AdminDataResponse, status_code=201)
async def create_admin_data(
    data: AdminDataCreate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    return await AdminDataCRUD.create(db, data)


@router.get("/", response_model=List[AdminDataResponse])
async def get_admin_data(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    return await AdminDataCRUD.get_all(db, skip, limit)


@router.get("/active", response_model=AdminDataResponse)
async def get_active_config(
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    data = await AdminDataCRUD.get_active(db)
    if not data:
        raise HTTPException(status_code=404, detail="No active configuration found")
    return data


@router.get("/{data_id}", response_model=AdminDataResponse)
async def get_admin_data_item(
    data_id: int,
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    data = await AdminDataCRUD.get(db, data_id)
    if not data:
        raise HTTPException(status_code=404, detail="Admin data not found")
    return data


@router.put("/{data_id}", response_model=AdminDataResponse)
async def update_admin_data(
    data_id: int,
    data: AdminDataUpdate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    updated = await AdminDataCRUD.update(db, data_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Admin data not found")
    return updated


@router.delete("/{data_id}", status_code=204)
async def delete_admin_data(
    data_id: int,
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    deleted = await AdminDataCRUD.delete(db, data_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Admin data not found")
    return None
