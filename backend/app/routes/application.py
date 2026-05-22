from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.core.database import get_db
from app.core.security import get_current_admin
from app.core.scoring import calculate_lead_score
from app.models.admin_user import AdminUserModel
from app.models.application import (
    ApplicationModel, ApplicationCreate, ApplicationUpdate,
    ApplicationResponse, ApplicationStatsResponse, ApplicationCRUD
)

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("/", response_model=ApplicationResponse, status_code=201)
async def create_application(
    data: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
):
    return await ApplicationCRUD.create(db, data)


@router.get("/", response_model=List[ApplicationResponse])
async def get_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    return await ApplicationCRUD.get_all(db, skip, limit)


@router.get("/scored", response_model=List[ApplicationResponse])
async def get_scored_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    result = await db.execute(
        select(ApplicationModel).order_by(ApplicationModel.id)
    )
    apps = result.scalars().all()

    scored = []
    for app in apps:
        app_dict = {c.name: getattr(app, c.name) for c in app.__table__.columns}
        scoring = calculate_lead_score(app_dict)
        resp = ApplicationResponse.model_validate(app)
        resp.scoring = scoring
        scored.append(resp)

    scored.sort(key=lambda x: x.scoring["score"], reverse=True)
    return scored[skip:skip + limit]


@router.get("/stats", response_model=ApplicationStatsResponse)
async def get_application_stats(
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    return await ApplicationCRUD.get_stats(db)


@router.get("/{app_id}", response_model=ApplicationResponse)
async def get_application(
    app_id: int,
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    app = await ApplicationCRUD.get_by_id(db, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    app_dict = {c.name: getattr(app, c.name) for c in app.__table__.columns}
    scoring = calculate_lead_score(app_dict)
    resp = ApplicationResponse.model_validate(app)
    resp.scoring = scoring
    return resp


@router.put("/{app_id}", response_model=ApplicationResponse)
async def update_application(
    app_id: int,
    data: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    updated = await ApplicationCRUD.update(db, app_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Application not found")
    app_dict = {c.name: getattr(updated, c.name) for c in updated.__table__.columns}
    scoring = calculate_lead_score(app_dict)
    resp = ApplicationResponse.model_validate(updated)
    resp.scoring = scoring
    return resp


@router.delete("/{app_id}", status_code=204)
async def delete_application(
    app_id: int,
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    app = await ApplicationCRUD.get_by_id(db, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    await db.delete(app)
    await db.commit()
    return None
