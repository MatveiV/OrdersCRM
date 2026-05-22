from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
from typing import Optional
from datetime import datetime

from app.core.database import Base
from app.core.security import hash_password, verify_password


"""
CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS idx_admin_users_username ON admin_users(username);
"""


class AdminUserModel(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(Text, default=lambda: datetime.now().isoformat())
    is_active = Column(Boolean, default=True)


class AdminUserCRUD:
    @staticmethod
    async def create_admin(db: AsyncSession, username: str, password: str) -> AdminUserModel:
        hashed = hash_password(password)
        admin = AdminUserModel(username=username, password_hash=hashed)
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        return admin

    @staticmethod
    async def get_admin_by_id(db: AsyncSession, admin_id: int) -> Optional[AdminUserModel]:
        result = await db.execute(select(AdminUserModel).where(AdminUserModel.id == admin_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_admin_by_username(db: AsyncSession, username: str) -> Optional[AdminUserModel]:
        result = await db.execute(select(AdminUserModel).where(AdminUserModel.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_admins(db: AsyncSession) -> list[AdminUserModel]:
        result = await db.execute(select(AdminUserModel))
        return result.scalars().all()

    @staticmethod
    async def update_admin(db: AsyncSession, admin_id: int, **kwargs) -> Optional[AdminUserModel]:
        admin = await AdminUserCRUD.get_admin_by_id(db, admin_id)
        if not admin:
            return None
        if "password" in kwargs:
            kwargs["password_hash"] = hash_password(kwargs.pop("password"))
        for key, value in kwargs.items():
            setattr(admin, key, value)
        await db.commit()
        await db.refresh(admin)
        return admin

    @staticmethod
    async def delete_admin(db: AsyncSession, admin_id: int) -> bool:
        admin = await AdminUserCRUD.get_admin_by_id(db, admin_id)
        if not admin:
            return False
        await db.delete(admin)
        await db.commit()
        return True

    @staticmethod
    async def get_admin_count(db: AsyncSession) -> int:
        result = await db.execute(select(AdminUserModel))
        return len(result.scalars().all())

    @staticmethod
    async def verify_password(db: AsyncSession, username: str, password: str) -> Optional[AdminUserModel]:
        admin = await AdminUserCRUD.get_admin_by_username(db, username)
        if not admin:
            return None
        if not verify_password(password, admin.password_hash):
            return None
        return admin
