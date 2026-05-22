# C4 Context Diagram — Orders CRM

**Уровень:** System Context (Level 1)
**Цель:** Показать систему и её взаимодействие с внешними акторами

```mermaid
C4Context
    title Orders CRM — System Context Diagram

    Person(customer, "Клиент", "Посетитель лендинга, заполняет форму заявки, поведенческие метрики")
    Person(admin, "Администратор", "Управляет заявками, услугами, через JWT-авторизацию")

    System_Boundary(orderscrm, "Orders CRM System (Docker)") {
        System(nginx, "Nginx", "Reverse proxy, SSL termination, статика, rate-limit")
        System(frontend_client, "Client Frontend", "Лендинг: Hero, проекты, форма + трекинг")
        System(frontend_admin, "Admin Frontend", "SPA: авторизация, услуги, заявки, статистика")
        System(backend, "Backend API", "FastAPI: CRUD, JWT, скоринг, метрики")
        SystemDb(postgres, "PostgreSQL", "crm_db: 7 таблиц")
        System_Ext(watchtower, "Watchtower", "Авто-обновление образов")
    }

    Rel(customer, nginx, "HTTPS: просматривает лендинг, отправляет заявку, трекинг")
    Rel(admin, nginx, "HTTPS: /admin: авторизация, управление")
    Rel(nginx, frontend_client, "Раздаёт статику /")
    Rel(nginx, frontend_admin, "Раздаёт статику /admin")
    Rel(nginx, backend, "Проксирует /api/*, /health; блокирует /docs")
    Rel(backend, postgres, "SQL: asyncpg, 7 моделей")
    Rel(backend, nginx, "JWT-токены через заголовки")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Описание акторов

| Актор | Роль | Взаимодействие |
|-------|------|----------------|
| Клиент | Посетитель | Заполняет форму, отправляет метрики поведения |
| Администратор | Управление | JWT-авторизация, CRUD услуг, просмотр заявок и статистики |

## Описание систем

| Система | Технология | Назначение |
|---------|------------|------------|
| Nginx | nginx:alpine | Reverse proxy, SSL, статика, rate-limit (10r/s) |
| Client Frontend | Vite + Vanilla JS | Лендинг + трекинг поведения (behavior-metrics.js) |
| Admin Frontend | Vite + Vanilla JS | SPA: 4 вкладки (услуги, лиды, CRM, статистика) |
| Backend API | FastAPI + SQLAlchemy | REST API, скоринг, JWT, агрегация метрик |
| PostgreSQL | postgres:16-alpine | 7 таблиц: leads, behaviors, admin_users, admin_data, admin_settings, applications, behavior_metrics |
| Watchtower | containrrr/watchtower | Автоматическое обновление Docker-образов |
