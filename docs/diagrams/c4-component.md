# C4 Component Diagram — Backend API

**Уровень:** Component (Level 3)
**Цель:** Показать компоненты Backend API

```mermaid
C4Component
    title Orders CRM — Backend API Components

    Container_Boundary(backend, "Backend API (FastAPI)") {
        Component(main, "main.py", "FastAPI App", "Точка входа, lifespan, CORS, 7 роутеров, disable_docs")

        Component(auth_router, "auth_router", "API Router", "/api/auth: register, login, refresh, check, me")
        Component(lead_router, "lead_router", "API Router", "/api/leads: CRUD + авто-создание Application")
        Component(behavior_router, "behavior_router", "API Router", "/api/behaviors: CRUD (1:1 с Lead)")
        Component(admin_router, "admin_router", "API Router", "/api/admin: AdminData + AdminSettings CRUD")
        Component(application_router, "application_router", "API Router", "/api/applications: scored, stats, CRUD")
        Component(metric_router, "metric_router", "API Router", "/api/behavior-metrics: POST + stats")
        Component(public_router, "public_router", "API Router", "/api/public: services (no auth)")

        Component(database, "database.py", "Database Module", "Async engine, session factory, init_db")

        Component(lead_model, "LeadModel", "SQLAlchemy Model", "leads + priority/status/planning/cost")
        Component(behavior_model, "BehaviorModel", "SQLAlchemy Model", "behaviors (1:1)")
        Component(admin_user_model, "AdminUserModel", "SQLAlchemy Model", "admin_users (JWT)")
        Component(admin_data_model, "AdminDataModel", "SQLAlchemy Model", "admin_data (UI config)")
        Component(admin_setting_model, "AdminSettingModel", "SQLAlchemy Model", "admin_settings (услуги)")
        Component(application_model, "ApplicationModel", "SQLAlchemy Model", "applications (CRM)")
        Component(metric_model, "BehaviorMetricModel", "SQLAlchemy Model", "behavior_metrics (INSERT-only)")

        Component(scoring, "scoring.py", "Core Module", "calculate_lead_score: 8 критериев, 100 баллов")
        Component(security, "security.py", "Core Module", "JWT create/verify, bcrypt, get_current_admin")
    }

    Rel(main, auth_router, "include_router", "/api/auth")
    Rel(main, lead_router, "include_router", "/api/leads")
    Rel(main, behavior_router, "include_router", "/api/behaviors")
    Rel(main, admin_router, "include_router", "/api/admin")
    Rel(main, application_router, "include_router", "/api/applications")
    Rel(main, metric_router, "include_router", "/api/behavior-metrics")
    Rel(main, public_router, "include_router", "/api/public")
    Rel(main, database, "lifespan", "init_db()")

    Rel(application_router, scoring, "вызывает", "calculate_lead_score()")
    Rel(auth_router, security, "вызывает", "JWT, bcrypt")
    Rel(lead_router, security, "вызывает", "get_current_admin")
    Rel(lead_router, application_model, "создаёт", "Application при создании Lead")

    UpdateLayoutConfig($c4ShapeInRow="5", $c4BoundaryInRow="1")
```

## Описание компонентов

| Компонент | Файл | Назначение |
|-----------|------|------------|
| main.py | app/main.py | FastAPI, CORS, lifespan, 7 роутеров, disable_docs |
| auth_router | app/routes/auth.py | POST register/login/refresh, GET check/me |
| lead_router | app/routes/lead.py | CRUD лидов + авто-создание Application |
| behavior_router | app/routes/behavior.py | CRUD поведений (1:1 с Lead) |
| admin_router | app/routes/admin.py | CRUD AdminData + AdminSettings |
| application_router | app/routes/application.py | CRUD + /scored + /stats для заявок |
| metric_router | app/routes/behavior_metric.py | POST метрик + GET /stats |
| public_router | app/routes/public.py | GET /api/public/services (без JWT) |
| database.py | app/core/database.py | Async engine, session factory |
| scoring.py | app/core/scoring.py | 8 критериев, 100 баллов, температура, инсайты |
| security.py | app/core/security.py | JWT (HS256), bcrypt, get_current_admin |
