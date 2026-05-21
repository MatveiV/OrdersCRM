# C4 Component Diagram — Backend API

**Уровень:** Component (Level 3)
**Цель:** Показать компоненты Backend API

```mermaid
C4Component
    title Orders CRM — Backend API Components

    Container_Boundary(backend, "Backend API (FastAPI)") {
        Component(main, "main.py", "FastAPI App", "Точка входа, lifespan, CORS, роутеры")
        Component(lead_router, "lead_router", "API Router", "CRUD операции с лидами")
        Component(behavior_router, "behavior_router", "API Router", "CRUD операции с поведениями")
        Component(admin_router, "admin_router", "API Router", "CRUD операций с настройками")
        Component(database, "database.py", "Database Module", "Async engine, session factory, init_db")
        Component(lead_model, "LeadModel", "SQLAlchemy Model", "Модель лида, LeadCreate, LeadResponse")
        Component(behavior_model, "BehaviorModel", "SQLAlchemy Model", "Модель поведения, BehaviorCreate")
        Component(admin_model, "AdminModel", "SQLAlchemy Model", "Модель настроек, AdminDataCreate")
        Component(lead_crud, "LeadCRUD", "CRUD Service", "create, get, get_all, update, delete")
        Component(behavior_crud, "BehaviorCRUD", "CRUD Service", "create, get, get_all, update, delete")
        Component(admin_crud, "AdminCRUD", "CRUD Service", "create, get, get_all, update, delete, get_active")
    }

    Rel(main, lead_router, "include_router", "/api/leads")
    Rel(main, behavior_router, "include_router", "/api/behaviors")
    Rel(main, admin_router, "include_router", "/api/admin")
    Rel(main, database, "lifespan", "init_db()")
    Rel(lead_router, lead_crud, "вызывает", "CRUD операции")
    Rel(behavior_router, behavior_crud, "вызывает", "CRUD операции")
    Rel(admin_router, admin_crud, "вызывает", "CRUD операции")
    Rel(lead_crud, lead_model, "использует", "LeadModel, LeadCreate")
    Rel(behavior_crud, behavior_model, "использует", "BehaviorModel, BehaviorCreate")
    Rel(admin_crud, admin_model, "использует", "AdminModel, AdminDataCreate")
    Rel(lead_crud, database, "использует", "AsyncSession")
    Rel(behavior_crud, database, "использует", "AsyncSession")
    Rel(admin_crud, database, "использует", "AsyncSession")

    UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="1")
```

## Описание компонентов

| Компонент | Файл | Назначение |
|-----------|------|------------|
| main.py | app/main.py | FastAPI приложение, lifespan, CORS middleware, агрегация роутеров |
| lead_router | app/routes/lead.py | POST /api/leads/, GET /api/leads/, GET /api/leads/{id}, PUT, DELETE |
| behavior_router | app/routes/behavior.py | POST /api/behaviors/, GET /api/behaviors/, GET /api/behaviors/{lead_id}, PUT, DELETE |
| admin_router | app/routes/admin.py | POST /api/admin/, GET /api/admin/, GET /api/admin/active, PUT, DELETE |
| database.py | app/core/database.py | Async engine, session factory, init_db(), Base |
| LeadModel | app/models/lead.py | SQLAlchemy модель + Pydantic схемы (LeadCreate, LeadUpdate, LeadResponse) |
| BehaviorModel | app/models/behavior.py | SQLAlchemy модель + Pydantic схемы |
| AdminModel | app/models/admin.py | SQLAlchemy модель + Pydantic схемы |
| LeadCRUD | app/models/lead.py | create, get, get_all, update, delete для лидов |
| BehaviorCRUD | app/models/behavior.py | create, get, get_all, update, delete для поведений |
| AdminCRUD | app/models/admin.py | create, get, get_all, update, delete, get_active для настроек |
