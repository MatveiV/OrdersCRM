from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.lead import (
    LeadCreate, LeadUpdate, LeadResponse, LeadCRUD
)
from app.models.application import ApplicationCreate, ApplicationCRUD
from app.models.admin_user import AdminUserModel

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.post("/", response_model=LeadResponse, status_code=201)
async def create_lead(lead: LeadCreate, db: AsyncSession = Depends(get_db)):
    db_lead = await LeadCRUD.create(db, lead)
    app_data = ApplicationCreate(
        first_name=lead.first_name,
        last_name=lead.last_name,
        middle_name=lead.middle_name,
        contact_data=lead.contact_data,
        business_niche=lead.business_niche,
        company_size=lead.company_size,
        task_volume=lead.task_volume,
        role=lead.role,
        business_info=lead.business_info,
        budget=lead.budget,
        project_deadline=lead.project_deadline,
        task_type=lead.task_type,
        product_interest=lead.product_interest,
        preferred_contact_method=lead.preferred_contact_method,
        convenient_time=lead.convenient_time,
        comment=lead.comment,
    )
    await ApplicationCRUD.create(db, app_data)
    return db_lead


@router.get("/", response_model=List[LeadResponse])
async def get_leads(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    return await LeadCRUD.get_all(db, skip, limit)


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    lead = await LeadCRUD.get(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    lead: LeadUpdate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    updated = await LeadCRUD.update(db, lead_id, lead)
    if not updated:
        raise HTTPException(status_code=404, detail="Lead not found")
    return updated


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    admin: AdminUserModel = Depends(get_current_admin),
):
    deleted = await LeadCRUD.delete(db, lead_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Lead not found")
    return None
