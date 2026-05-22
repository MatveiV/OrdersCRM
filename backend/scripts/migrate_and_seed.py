"""
Migration + seed script: adds new columns to 'leads' table
and populates 'admin_settings' with development services.

Usage: docker exec -i orderscrm_backend python3 scripts/migrate_and_seed.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from sqlalchemy import text
from app.core.database import engine, async_session_factory
from app.models.admin_settings import AdminSettingCRUD


MIGRATIONS = [
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'medium'",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'new'",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS planned_start_date TEXT",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS planned_end_date TEXT",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS assigned_to VARCHAR(255)",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS estimated_cost INTEGER",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS actual_cost INTEGER",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS payment_status VARCHAR(20) DEFAULT 'unpaid'",
]

SERVICES = [
    {
        "service_name": "Разработка MVP (Minimum Viable Product)",
        "task_type": "Разработка",
        "product_interest": "MVP",
        "budget_range": '{"min": 500000, "max": 3000000, "step": 100000}',
        "description": "Быстрый запуск минимально жизнеспособного продукта для проверки гипотез: от 4 до 12 недель.",
        "is_active": True,
    },
    {
        "service_name": "Web-приложение (CRM / ERP / Dashboard)",
        "task_type": "Разработка",
        "product_interest": "Web-приложение",
        "budget_range": '{"min": 800000, "max": 5000000, "step": 200000}',
        "description": "Полноценное веб-приложение с бэкендом, авторизацией, отчётами — React/Vue/Python/Go.",
        "is_active": True,
    },
    {
        "service_name": "Telegram / Discord бот (AI-агент)",
        "task_type": "Разработка",
        "product_interest": "Чат-бот",
        "budget_range": '{"min": 150000, "max": 1500000, "step": 50000}',
        "description": "Интеграция с LLM (GPT/Claude), диалоговые сценарии, внешние API, админ-панель.",
        "is_active": True,
    },
    {
        "service_name": "Архитектура и ревью кода",
        "task_type": "Консалтинг",
        "product_interest": "Аудит",
        "budget_range": '{"min": 50000, "max": 300000, "step": 10000}',
        "description": "Аудит архитектуры, code review, оптимизация производительности, план рефакторинга.",
        "is_active": True,
    },
    {
        "service_name": "FinTech / Торговая платформа",
        "task_type": "Разработка",
        "product_interest": "FinTech",
        "budget_range": '{"min": 2000000, "max": 15000000, "step": 500000}',
        "description": "Расчётные системы, маркет-данные, low-latency трейдинг, интеграция с биржами.",
        "is_active": True,
    },
    {
        "service_name": "AI-интеграция и LLM-пайплайны",
        "task_type": "Разработка",
        "product_interest": "AI / LLM",
        "budget_range": '{"min": 300000, "max": 3000000, "step": 100000}',
        "description": "RAG-пайплайны, агентные системы, embedding-поиск, fine-tuning, стриминг.",
        "is_active": True,
    },
    {
        "service_name": "DevOps / CI/CD инфраструктура",
        "task_type": "Инфраструктура",
        "product_interest": "DevOps",
        "budget_range": '{"min": 100000, "max": 1000000, "step": 50000}',
        "description": "Docker, Kubernetes, CI/CD (GitHub Actions), мониторинг, логи, секьюрность.",
        "is_active": True,
    },
    {
        "service_name": "API Gateway / Микросервисная архитектура",
        "task_type": "Разработка",
        "product_interest": "API",
        "budget_range": '{"min": 500000, "max": 4000000, "step": 200000}',
        "description": "Проектирование и реализация API-гейтвеев, микросервисов, async-коммуникации (Kafka/RabbitMQ).",
        "is_active": True,
    },
    {
        "service_name": "Консультация и стратегия (1 час)",
        "task_type": "Консалтинг",
        "product_interest": "Стратегия",
        "budget_range": '{"min": 5000, "max": 15000, "step": 1000}',
        "description": "Часовая консультация по архитектуре, стеку технологий, планированию проекта.",
        "is_active": True,
    },
    {
        "service_name": "Data Pipeline / ETL / Аналитика",
        "task_type": "Разработка",
        "product_interest": "Данные",
        "budget_range": '{"min": 400000, "max": 3000000, "step": 100000}',
        "description": "Построение пайплайнов данных, ETL, OLAP-хранилища, дашборды (Superset/Grafana).",
        "is_active": True,
    },
]


async def run_migrations():
    async with engine.begin() as conn:
        for sql in MIGRATIONS:
            try:
                await conn.execute(text(sql))
                print(f"  OK: {sql[:60]}...")
            except Exception as e:
                print(f"  SKIP ({e}): {sql[:60]}...")


async def seed_services():
    async with async_session_factory() as db:
        existing = await AdminSettingCRUD.get_all(db)
        existing_names = {s.service_name for s in existing}
        new_count = 0
        for svc in SERVICES:
            if svc["service_name"] not in existing_names:
                await AdminSettingCRUD.create(db, svc)
                print(f"  + {svc['service_name']}")
                new_count += 1
            else:
                print(f"  = {svc['service_name']} (already exists)")
        print(f"\n  Added {new_count} new services, {len(existing)} already existed.")


async def main():
    print("=== Migration: adding new columns to 'leads' ===")
    await run_migrations()
    print()
    print("=== Seeding: admin_settings with development services ===")
    await seed_services()
    print()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
