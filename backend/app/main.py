import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import init_db
from app.routes.lead import router as lead_router
from app.routes.behavior import router as behavior_router
from app.routes.admin import router as admin_router
from app.routes.auth import router as auth_router
from app.routes.public import router as public_router
from app.routes.behavior_metric import router as behavior_metric_router
from app.routes.application import router as application_router

disable_docs = os.getenv("DISABLE_DOCS", "false").lower() == "true"
cors_origins = os.getenv("CORS_ORIGINS", "https://orderscrm.ru").split(",")
environment = os.getenv("ENVIRONMENT", "development")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Orders CRM Backend",
    description="Private CRM backend for lead management",
    version="1.2.0",
    docs_url=None if disable_docs else "/docs",
    redoc_url=None if disable_docs else "/redoc",
    openapi_url=None if disable_docs else "/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(lead_router, prefix="/api")
app.include_router(behavior_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(public_router, prefix="/api")
app.include_router(behavior_metric_router, prefix="/api")
app.include_router(application_router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
