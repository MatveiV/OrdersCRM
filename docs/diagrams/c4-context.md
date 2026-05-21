# C4 Context Diagram — Orders CRM

**Уровень:** System Context (Level 1)
**Цель:** Показать систему и её взаимодействие с внешними акторами

```mermaid
C4Context
    title Orders CRM — System Context Diagram

    Person(customer, "Клиент", "Посетитель лендинга, заполняет форму заявки")
    Person(admin, "Администратор", "Управляет лидами, настройками, БД через pgAdmin")
    Person(devops, "DevOps инженер", "Управляет деплоем, образами, SSL")

    System_Boundary(orderscrm, "Orders CRM System") {
        System(nginx, "Nginx", "Reverse proxy, SSL termination, статика")
        System(frontend_client, "Client Frontend", "Лендинг: Hero, проекты, форма заявки")
        System(frontend_admin, "Admin Frontend", "Админ-панель: форма заявки")
        System(backend, "Backend API", "FastAPI: CRUD лидов, поведений, настроек")
        SystemDb(postgres, "PostgreSQL", "crm_db: leads, behaviors, admin_data")
        System_Ext(pgadmin, "pgAdmin", "Веб-интерфейс управления БД")
        System_Ext(registry, "Docker Registry", "Локальный реестр образов")
    }

    Rel(customer, nginx, "HTTPS: просматривает лендинг, отправляет заявку")
    Rel(admin, pgadmin, "HTTPS:5050: управляет БД")
    Rel(admin, frontend_admin, "HTTPS: /admin: просматривает заявки")
    Rel(devops, registry, "HTTPS:8080: пушит/пуллит образы")
    Rel(nginx, frontend_client, "Раздаёт статику /")
    Rel(nginx, frontend_admin, "Раздаёт статику /admin")
    Rel(nginx, backend, "Проксирует /api/*, /docs, /health")
    Rel(backend, postgres, "SQL: asyncpg, CRUD операции")
    Rel(pgadmin, postgres, "SQL: управление БД")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Описание акторов

| Актор | Роль | Взаимодействие |
|-------|------|----------------|
| Клиент | Посетитель | Заполняет форму на лендинге, отправляет заявку |
| Администратор | Управление | Просматривает заявки через /admin, управляет БД через pgAdmin |
| DevOps | Инфраструктура | Деплой, SSL, Docker Registry |

## Описание систем

| Система | Технология | Назначение |
|---------|------------|------------|
| Nginx | nginx:alpine | Reverse proxy, SSL, раздача статики |
| Client Frontend | Vite + Vanilla JS | Лендинг с формой заявки |
| Admin Frontend | Vite + Vanilla JS | Админ-панель |
| Backend API | FastAPI + SQLAlchemy | REST API для лидов и поведений |
| PostgreSQL | postgres:16-alpine | Хранение данных |
| pgAdmin | dpage/pgadmin4 | Управление БД |
| Docker Registry | registry:2 | Локальный реестр образов |
