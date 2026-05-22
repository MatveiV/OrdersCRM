from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.models.admin_settings import AdminSettingModel, AdminSettingCRUD
from app.schemas.admin import AdminSettingResponse

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/services", response_model=List[AdminSettingResponse])
async def get_public_services(
    db: AsyncSession = Depends(get_db),
):
    settings = await AdminSettingCRUD.get_all(db)
    return [s for s in settings if s.is_active]
