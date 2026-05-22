"""
Migration script: create applications table and seed 10 test applications.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from sqlalchemy import text
from app.core.database import engine, async_session_factory
from app.models.application import ApplicationModel, ApplicationCreate, ApplicationCRUD

MIGRATIONS = [
    """
    CREATE TABLE IF NOT EXISTS applications (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(255) NOT NULL,
        last_name VARCHAR(255) NOT NULL,
        middle_name VARCHAR(255),
        contact_data TEXT NOT NULL,
        business_niche VARCHAR(255),
        company_size VARCHAR(100),
        task_volume VARCHAR(255),
        role VARCHAR(100),
        business_info TEXT,
        budget VARCHAR(100),
        project_deadline VARCHAR(255),
        task_type VARCHAR(255),
        product_interest VARCHAR(255),
        preferred_contact_method VARCHAR(100),
        convenient_time VARCHAR(100),
        comment TEXT,
        status VARCHAR(50) DEFAULT 'Новая',
        created_at TEXT DEFAULT NOW()
    )
    """,
]

SEED_DATA = [
    # --- 4 HOT (score >= 70) ---
    # 1. High budget + CEO
    ApplicationCreate(
        first_name="Иван", last_name="Петров", middle_name="Сергеевич",
        contact_data="+79001234567, ivan@fintech.ru",
        business_niche="FinTech", company_size="Крупная (500+)",
        task_volume="Разработка торговой платформы", role="Руководитель",
        business_info="Крупный fintech-холдинг, более 2000 сотрудников, 5 офисов",
        budget='{"min": 500000, "max": 2000000, "step": 100000}',
        project_deadline="2 недели", task_type="Разработка",
        product_interest="Торговая платформа",
        preferred_contact_method="telegram", convenient_time="10:00-18:00",
        comment="Срочно нужен MVP торговой платформы для запуска в следующем квартале. Готовы обсуждать детали и финансирование.",
    ),
    # 2. Urgent deadline + large company FinTech
    ApplicationCreate(
        first_name="Анна", last_name="Смирнова", middle_name="Викторовна",
        contact_data="anna.smirnova@bank.ru, +79007654321",
        business_niche="Банки", company_size="Крупная (500+)",
        task_volume="Внедрение AI-агента в колл-центр", role="Директор департамента",
        business_info="Крупный банк, 8000 сотрудников, отдел цифровой трансформации",
        budget='{"min": 1000000, "max": 5000000, "step": 500000}',
        project_deadline="ASAP", task_type="Разработка",
        product_interest="AI / LLM",
        preferred_contact_method="phone", convenient_time="09:00-20:00",
        comment="Критично важно запустить AI-агента в колл-центр до конца квартала. Бюджет согласован.",
    ),
    # 3. Big volume + full contacts + detailed comment
    ApplicationCreate(
        first_name="Олег", last_name="Иванов", middle_name="Дмитриевич",
        contact_data="o.ivanov@it-company.ru, +79001112233",
        business_niche="IT-услуги", company_size="Средняя (51-200)",
        task_volume="Миграция микросервисной архитектуры", role="Team Lead",
        business_info="Разрабатываем SaaS-продукты для ритейла, 150 сотрудников",
        budget='{"min": 200000, "max": 800000, "step": 50000}',
        project_deadline="3 недели", task_type="Инфраструктура",
        product_interest="API Gateway",
        preferred_contact_method="telegram", convenient_time="11:00-19:00",
        comment="Планируем мигрировать с монолита на микросервисы. Нужен аудит текущей архитектуры и план миграции. Бюджет можно увеличить при необходимости.",
    ),
    # 4. Medium budget + Director + FinTech + urgent
    ApplicationCreate(
        first_name="Мария", last_name="Козлова", middle_name="Алексеевна",
        contact_data="m.kozlova@finance.ru, +79009876543",
        business_niche="Финансы", company_size="Малая (11-50)",
        task_volume="Разработка дашборда для аналитики", role="Директор",
        business_info="Финансовая компания, 30 сотрудников, управление активами",
        budget='{"min": 300000, "max": 500000, "step": 50000}',
        project_deadline="1 неделя", task_type="Разработка",
        product_interest="Web-приложение",
        preferred_contact_method="telegram", convenient_time="10:00-17:00",
        comment="Срочно нужен дашборд для отчётов перед инвесторами. Желательно на следующей неделе.",
    ),
    # --- 3 WARM (score 40-69) ---
    # 5. Medium budget, mid-size, average deadline
    ApplicationCreate(
        first_name="Пётр", last_name="Сидоров", middle_name="Николаевич",
        contact_data="psidorov@retail.ru",
        business_niche="Ритейл", company_size="Малая (11-50)",
        task_volume="Разработка CRM для магазина", role="Менеджер",
        business_info="Сеть розничных магазинов, 40 сотрудников",
        budget='{"min": 100000, "max": 300000, "step": 25000}',
        project_deadline="1 месяц", task_type="Разработка",
        product_interest="CRM",
        preferred_contact_method="email", convenient_time="09:00-18:00",
        comment="Хотим автоматизировать учёт клиентов и заказов.",
    ),
    # 6. Low-medium budget, startup, no comment
    ApplicationCreate(
        first_name="Елена", last_name="Кузнецова", middle_name="Павловна",
        contact_data="elena@startup.io",
        business_niche="IT-стартап", company_size="Микро (1-10)",
        task_volume="MVP мобильного приложения", role="Founder",
        business_info="Стартап на стадии pre-seed, 5 человек",
        budget='{"min": 50000, "max": 150000, "step": 10000}',
        project_deadline="2 месяца", task_type="Разработка",
        product_interest="Web-приложение",
        preferred_contact_method="telegram", convenient_time="15:00-20:00",
        comment=None,
    ),
    # 7. No budget info, mid company, IT niche
    ApplicationCreate(
        first_name="Дмитрий", last_name="Новиков", middle_name="Игоревич",
        contact_data="d.novikov@telecom.ru, +79005556677",
        business_niche="Телеком", company_size="Средняя (51-200)",
        task_volume="Оптимизация сети", role="Специалист",
        business_info="Телеком-оператор, региональный офис",
        budget=None,
        project_deadline="3 месяца", task_type="Инфраструктура",
        product_interest="DevOps",
        preferred_contact_method="email", convenient_time="09:00-18:00",
        comment="Нужна консультация по оптимизации инфраструктуры.",
    ),
    # --- 3 COLD (score 0-39) ---
    # 8. Small budget, micro company, no comment, long deadline
    ApplicationCreate(
        first_name="Сергей", last_name="Морозов", middle_name="Андреевич",
        contact_data="morozov@mail.ru",
        business_niche="Прочее", company_size="Микро (1-10)",
        task_volume="Простой сайт", role="Сотрудник",
        business_info="Небольшой интернет-магазин",
        budget='{"min": 10000, "max": 30000, "step": 5000}',
        project_deadline="6 месяцев", task_type="Разработка",
        product_interest="Web-приложение",
        preferred_contact_method="email", convenient_time=None,
        comment="Хочу сайт",
    ),
    # 9. Minimal data, no comment, weak signals
    ApplicationCreate(
        first_name="Алексей", last_name="Васильев", middle_name=None,
        contact_data="alex@example.com",
        business_niche=None, company_size=None,
        task_volume=None, role=None,
        business_info=None,
        budget=None,
        project_deadline=None, task_type=None,
        product_interest=None,
        preferred_contact_method="email", convenient_time=None,
        comment=None,
    ),
    # 10. Tiny budget, individual, no comment
    ApplicationCreate(
        first_name="Наталья", last_name="Белова", middle_name=None,
        contact_data="+79000000001",
        business_niche="Образование", company_size="Микро (1-10)",
        task_volume="Небольшой лендинг", role="Специалист",
        business_info="Репетиторский центр",
        budget='{"min": 5000, "max": 15000, "step": 5000}',
        project_deadline="год", task_type="Разработка",
        product_interest="Web-приложение",
        preferred_contact_method="phone", convenient_time="09:00-12:00",
        comment="Нужен сайт для репетиторского центра",
    ),
]


async def run_migrations():
    async with engine.begin() as conn:
        for sql in MIGRATIONS:
            try:
                await conn.execute(text(sql))
                print(f"  OK: {sql[:70]}...")
            except Exception as e:
                print(f"  SKIP ({e}): {sql[:70]}...")


async def seed_applications():
    async with async_session_factory() as db:
        existing = await ApplicationCRUD.get_all(db)
        if len(existing) >= 10:
            print(f"  Already {len(existing)} applications, skipping seed.")
            return
        for app_data in SEED_DATA:
            await ApplicationCRUD.create(db, app_data)
            print(f"  + {app_data.first_name} {app_data.last_name}")

    async with async_session_factory() as db:
        total = len(await ApplicationCRUD.get_all(db))
        print(f"\n  Total applications: {total}")

    # Show scores
    from app.core.scoring import calculate_lead_score
    async with async_session_factory() as db:
        apps = await ApplicationCRUD.get_all(db)
        print(f"\n  Scoring summary:")
        for app in apps:
            d = {c.name: getattr(app, c.name) for c in app.__table__.columns}
            s = calculate_lead_score(d)
            label = {"hot": "HOT", "warm": "WARM", "cold": "COLD"}[s["temperature"]]
            print(f"  [{label:5s}] {app.first_name} {app.last_name:15s} score={s['score']:3d}  dept={s['recommended_department']}")


async def main():
    print("=== Migration: creating 'applications' table ===")
    await run_migrations()
    print()
    print("=== Seeding: 10 test applications ===")
    await seed_applications()
    print()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
