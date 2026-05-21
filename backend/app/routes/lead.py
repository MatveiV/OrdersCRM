from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.models.lead import (
    LeadCreate, LeadUpdate, LeadResponse, LeadCRUD
)

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.post("/", response_model=LeadResponse, status_code=201)
async def create_lead(lead: LeadCreate, db: AsyncSession = Depends(get_db)):
    return await LeadCRUD.create(db, lead)


@router.get("/", response_model=List[LeadResponse])
async def get_leads(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await LeadCRUD.get_all(db, skip, limit)


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: int, db: AsyncSession = Depends(get_db)):
    lead = await LeadCRUD.get(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(lead_id: int, lead: LeadUpdate, db: AsyncSession = Depends(get_db)):
    updated = await LeadCRUD.update(db, lead_id, lead)
    if not updated:
        raise HTTPException(status_code=404, detail="Lead not found")
    return updated


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(lead_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await LeadCRUD.delete(db, lead_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Lead not found")
    return None
