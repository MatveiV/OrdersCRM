from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import (
    create_access_token, create_refresh_token, decode_token,
    get_current_admin
)
from app.models.admin_user import AdminUserCRUD, AdminUserModel

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=255)


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AdminMeResponse(BaseModel):
    id: int
    username: str
    created_at: str
    is_active: bool

    class Config:
        from_attributes = True


def _generate_tokens(admin: AdminUserModel) -> dict:
    access_token = create_access_token({"sub": str(admin.id), "username": admin.username})
    refresh_token = create_refresh_token({"sub": str(admin.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    count = await AdminUserCRUD.get_admin_count(db)
    if count > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Регистрация закрыта, администратор уже существует",
        )
    existing = await AdminUserCRUD.get_admin_by_username(db, req.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином уже существует",
        )
    admin = await AdminUserCRUD.create_admin(db, req.username, req.password)
    return _generate_tokens(admin)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    admin = await AdminUserCRUD.verify_password(db, req.username, req.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Учётная запись деактивирована",
        )
    return _generate_tokens(admin)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(req: RefreshRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(req.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    admin_id = payload.get("sub")
    if admin_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    admin = await AdminUserCRUD.get_admin_by_id(db, int(admin_id))
    if not admin or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found or inactive",
        )
    return _generate_tokens(admin)


@router.get("/check")
async def check_admins(db: AsyncSession = Depends(get_db)):
    count = await AdminUserCRUD.get_admin_count(db)
    return {"has_admins": count > 0, "count": count}


@router.get("/me", response_model=AdminMeResponse)
async def get_me(admin: AdminUserModel = Depends(get_current_admin)):
    return admin
