# C4 Container Diagram — Orders CRM

**Уровень:** Container (Level 2)
**Цель:** Показать контейнеры системы и их взаимодействие

```mermaid
C4Container
    title Orders CRM — Container Diagram

    Person(customer, "Клиент", "Посетитель лендинга")
    Person(admin, "Администратор", "Управление системой")

    System_Boundary(docker, "Docker Host (185.87.48.13)") {
        Container(nginx, "Nginx", "nginx:alpine", "Reverse proxy, SSL, статика")
        Container(frontend_client, "Client Frontend", "Vite + Vanilla JS", "Лендинг: Hero, проекты, форма")
        Container(frontend_admin, "Admin Frontend", "Vite + Vanilla JS", "Админ-панель")
        Container(backend, "Backend API", "Python 3.12 + FastAPI", "REST API, бизнес-логика")
        ContainerDb(postgres, "PostgreSQL", "postgres:16-alpine", "crm_db")
        Container(pgadmin, "pgAdmin", "dpage/pgadmin4", "Веб-интерфейс БД")
        Container(registry, "Docker Registry", "registry:2", "Локальный реестр")
    }

    Rel(customer, nginx, "HTTPS:443", "Просмотр лендинга, отправка формы")
    Rel(admin, nginx, "HTTPS:443", "Доступ к /admin, /docs")
    Rel(admin, pgadmin, "HTTPS:5050", "Управление БД")
    Rel(nginx, frontend_client, "Внутренний", "Раздача статики /")
    Rel(nginx, frontend_admin, "Внутренний", "Раздача статики /admin")
    Rel(nginx, backend, "HTTP:8000", "Прокси /api/*, /docs, /health")
    Rel(frontend_client, backend, "HTTP через Nginx", "GET /api/admin/active, POST /api/leads/")
    Rel(frontend_admin, backend, "HTTP через Nginx", "GET /api/admin/active, POST /api/leads/")
    Rel(backend, postgres, "TCP:5432", "asyncpg: CRUD операции")
    Rel(pgadmin, postgres, "TCP:5432", "SQL: управление БД")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Описание контейнеров

| Контейнер | Технология | Порт | Назначение |
|-----------|------------|------|------------|
| Nginx | nginx:alpine | 80, 443 | Reverse proxy, SSL termination, раздача статики |
| Client Frontend | Vite + Vanilla JS | - | Лендинг: Hero-секция, портфолио, форма заявки |
| Admin Frontend | Vite + Vanilla JS | - | Админ-панель (старая форма) |
| Backend API | Python 3.12 + FastAPI | 8000 (внутренний) | REST API, валидация, бизнес-логика |
| PostgreSQL | postgres:16-alpine | 5432 (внутренний) | Хранение лидов, поведений, настроек |
| pgAdmin | dpage/pgadmin4 | 5050 | Веб-интерфейс для управления БД |
| Docker Registry | registry:2 | 8080 | Локальный реестр Docker-образов |

## Потоки данных

1. **Клиент → Лендинг:** HTTPS запрос → Nginx → Client Frontend (статика)
2. **Клиент → Форма:** Заполнение формы → POST /api/leads/ → Nginx → Backend → PostgreSQL
3. **Админ → /admin:** HTTPS запрос → Nginx → Admin Frontend (статика)
4. **Админ → /docs:** HTTPS запрос → Nginx → Backend (Swagger UI)
5. **Backend → PostgreSQL:** asyncpg подключение → SQL запросы → результаты
