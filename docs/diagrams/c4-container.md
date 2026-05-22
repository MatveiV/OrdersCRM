# C4 Container Diagram — Orders CRM

**Уровень:** Container (Level 2)
**Цель:** Показать контейнеры системы и их взаимодействие

```mermaid
C4Container
    title Orders CRM — Container Diagram

    Person(customer, "Клиент", "Посетитель лендинга")
    Person(admin, "Администратор", "Управление системой")

    System_Boundary(docker, "Docker Host (185.87.48.13)") {
        Container(nginx, "Nginx", "nginx:alpine", "Reverse proxy, SSL, статика, rate-limit, блокировка /docs")
        Container(frontend_client, "Client Frontend", "Vite + Vanilla JS", "Лендинг + трекинг поведения")
        Container(frontend_admin, "Admin Frontend", "Vite + Vanilla JS", "SPA: 4 вкладки, JWT-авторизация")
        Container(backend, "Backend API", "Python 3.12 + FastAPI", "REST API, JWT, скоринг, 7 моделей")
        ContainerDb(postgres, "PostgreSQL", "postgres:16-alpine", "crm_db: 7 таблиц")
        Container(watchtower, "Watchtower", "containrrr/watchtower", "Авто-обновление")
    }

    Rel(customer, nginx, "HTTPS:443", "Лендинг, форма, трекинг")
    Rel(admin, nginx, "HTTPS:443", "/admin — SPA")
    Rel(nginx, frontend_client, "Внутренний", "Статика /")
    Rel(nginx, frontend_admin, "Внутренний", "Статика /admin")
    Rel(nginx, backend, "HTTP:8000", "Прокси /api/*, /health; 403 на /docs")
    Rel(frontend_client, backend, "HTTP через Nginx", "POST /api/leads, POST /api/behavior-metrics, GET /api/public/services")
    Rel(frontend_admin, backend, "HTTP через Nginx", "JWT: /api/auth/*, /api/applications/*, /api/admin/*")
    Rel(backend, postgres, "TCP:5432", "asyncpg: 7 таблиц")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Описание контейнеров

| Контейнер | Технология | Порт | Назначение |
|-----------|------------|------|------------|
| Nginx | nginx:alpine | 80, 443 | Reverse proxy, SSL, rate-limit (10r/s), security headers, блокировка /docs |
| Client Frontend | Vite + Vanilla JS | — | Лендинг: Hero, портфолио, форма + трекинг поведения |
| Admin Frontend | Vite + Vanilla JS | — | SPA: 4 вкладки, JWT, модалки, toast-уведомления |
| Backend API | Python 3.12 + FastAPI | 8000 (внутр.) | 7 роутеров, JWT, скоринг (8 критериев), агрегация |
| PostgreSQL | postgres:16-alpine | 5432 (внутр.) | leads, behaviors, admin_users, admin_data, admin_settings, applications, behavior_metrics |
| Watchtower | containrrr/watchtower | — | Авто-обновление по расписанию |

## Потоки данных

1. **Клиент → Лендинг:** HTTPS → Nginx → статика (Client Frontend)
2. **Клиент → Форма:** POST /api/leads/ → Nginx → Backend → PostgreSQL (Lead + Application)
3. **Клиент → Метрики:** POST /api/behavior-metrics/ → Nginx → Backend → PostgreSQL
4. **Админ → /admin:** HTTPS → Nginx → Admin Frontend (SPA)
5. **Админ → JWT:** POST /api/auth/login → Nginx → Backend → JWT tokens
6. **Админ → API:** JWT-запросы → Nginx → Backend (verify JWT) → PostgreSQL
