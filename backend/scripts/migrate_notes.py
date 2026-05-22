import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://crm_user:crm_password@postgres:5432/crm_db"
)

engine = create_async_engine(DATABASE_URL)


async def main():
    async with engine.begin() as conn:
        await conn.execute(text("""
            ALTER TABLE applications
            ADD COLUMN IF NOT EXISTS notes TEXT DEFAULT ''
        """))
        print("OK: notes column added to applications")


asyncio.run(main())
