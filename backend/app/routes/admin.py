from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.admin import (
    AdminDataCreate, AdminDataUpdate, AdminDataResponse, AdminDataCRUD
)
from app.models.admin_settings import AdminSettingModel, AdminSettingCRUD
from app.models.admin_user import AdminUserModel
from app.schemas.admin import (
    AdminSettingCreate, AdminSettingUpdate, AdminSettingResponse
)

router = APIRouter(prefix="/admin", tags=["Admin"])


# ---- Service CRUD ----

@router.get("/services", response_model=List[AdminSettingResponse])
async def get_services(
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    return await AdminSettingCRUD.get_all(db)


@router.post("/services", response_model=AdminSettingResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    data: AdminSettingCreate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    return await AdminSettingCRUD.create(db, data.model_dump())


@router.get("/services/{service_id}", response_model=AdminSettingResponse)
async def get_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    setting = await AdminSettingCRUD.get_by_id(db, service_id)
    if not setting:
        raise HTTPException(status_code=404, detail="Service not found")
    return setting


@router.put("/services/{service_id}", response_model=AdminSettingResponse)
async def update_service(
    service_id: int,
    data: AdminSettingUpdate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    updated = await AdminSettingCRUD.update(db, service_id, data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Service not found")
    return updated


@router.delete("/services/{service_id}")
async def delete_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    deleted = await AdminSettingCRUD.delete(db, service_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"success": True, "message": "Услуга удалена"}


# ---- AdminData CRUD (existing) ----

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
