from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import init_db
from app.routes.lead import router as lead_router
from app.routes.behavior import router as behavior_router
from app.routes.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Orders CRM Backend",
    description="Private CRM backend for lead management",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lead_router, prefix="/api")
app.include_router(behavior_router, prefix="/api")
app.include_router(admin_router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
