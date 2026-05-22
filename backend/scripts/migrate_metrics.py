"""
Migration script to create behavior_metrics table and fix any constraints.

Usage: docker exec orderscrm_backend python3 scripts/migrate_metrics.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from sqlalchemy import text
from app.core.database import engine, async_session_factory
from app.models.behavior_metric import BehaviorMetricModel


MIGRATIONS = [
    # Create the behavior_metrics table
    """
    CREATE TABLE IF NOT EXISTS behavior_metrics (
        id SERIAL PRIMARY KEY,
        application_id INTEGER DEFAULT 0,
        time_on_page INTEGER DEFAULT 0,
        buttons_clicked TEXT,
        cursor_positions TEXT,
        return_frequency INTEGER DEFAULT 0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    )
    """,
    # Drop any foreign key if exists
    "ALTER TABLE behavior_metrics DROP CONSTRAINT IF EXISTS fk_behavior_metrics_application",
    # Drop unique index if exists
    "DROP INDEX IF EXISTS idx_behavior_metrics_app_id",
    # Ensure columns are nullable with defaults
    "ALTER TABLE behavior_metrics ALTER COLUMN application_id SET DEFAULT 0",
    "ALTER TABLE behavior_metrics ALTER COLUMN time_on_page SET DEFAULT 0",
    "ALTER TABLE behavior_metrics ALTER COLUMN return_frequency SET DEFAULT 0",
]


async def run_migrations():
    async with engine.begin() as conn:
        for sql in MIGRATIONS:
            try:
                await conn.execute(text(sql))
                print(f"  OK: {sql[:70]}...")
            except Exception as e:
                print(f"  SKIP ({e}): {sql[:70]}...")

    print()
    print("  Migration complete.")


if __name__ == "__main__":
    asyncio.run(run_migrations())
