from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
import asyncpg
import os

app = FastAPI(title="Orders CRM Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://crm_user:crm_password@postgres:5432/crm_db"
)

pool: Optional[asyncpg.Pool] = None

async def get_db():
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=2,
            max_size=10
        )
    return pool

class LeadCreate(BaseModel):
    contact_name: str
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    business_info: Optional[str] = None
    budget: Optional[str] = None
    contact_method: Optional[str] = None
    comments: Optional[str] = None
    lead_metrics: Optional[Dict[str, Any]] = None
    technical_info: Optional[Dict[str, Any]] = None
    source_url: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None

class LeadResponse(BaseModel):
    id: int
    created_at: datetime
    contact_name: str

@app.post("/api/leads", response_model=LeadResponse)
async def create_lead(lead: LeadCreate, request: Request):
    pool = await get_db()
    
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            """
            INSERT INTO leads (
                contact_name, contact_phone, contact_email,
                business_info, budget, contact_method, comments,
                lead_metrics, technical_info, source_url,
                utm_source, utm_medium, utm_campaign,
                ip_address, user_agent, created_at
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                $11, $12, $13, $14, $15, NOW()
            ) RETURNING id, created_at, contact_name
            """,
            lead.contact_name,
            lead.contact_phone,
            lead.contact_email,
            lead.business_info,
            lead.budget,
            lead.contact_method,
            lead.comments,
            str(lead.lead_metrics) if lead.lead_metrics else None,
            str(lead.technical_info) if lead.technical_info else None,
            lead.source_url,
            lead.utm_source,
            lead.utm_medium,
            lead.utm_campaign,
            ip_address,
            user_agent
        )
    
    return LeadResponse(**result)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)