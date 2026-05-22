# Orders CRM Backend

FastAPI-бэкенд для CRM-системы управления заявками с интеллектуальным скорингом и сбором поведенческих метрик.

## Архитектура

```
backend/
├── app/
│   ├── main.py                    # FastAPI приложение, CORS, lifespan
│   ├── core/
│   │   ├── database.py            # async engine, session factory, init_db
│   │   ├── scoring.py             # Интеллектуальный скоринг (8 критериев)
│   │   └── security.py            # JWT (access/refresh), bcrypt
│   ├── models/
│   │   ├── lead.py                # LeadModel + CRUD (сырые заявки)
│   │   ├── behavior.py            # BehaviorModel + CRUD (1:1 с Lead)
│   │   ├── admin.py               # AdminDataModel + CRUD (настройки UI)
│   │   ├── admin_user.py          # AdminUserModel + CRUD (JWT-админы)
│   │   ├── admin_settings.py      # AdminSettingModel + CRUD (услуги)
│   │   ├── application.py         # ApplicationModel + CRUD + stats (CRM)
│   │   └── behavior_metric.py     # BehaviorMetricModel + stats (метрики)
│   ├── routes/
│   │   ├── lead.py                # /api/leads/* (Lead → Application авто)
│   │   ├── behavior.py            # /api/behaviors/*
│   │   ├── admin.py               # /api/admin/* (AdminData)
│   │   ├── auth.py                # /api/auth/* (register, login, refresh)
│   │   ├── application.py         # /api/applications/* (scored, stats)
│   │   ├── behavior_metric.py     # /api/behavior-metrics/* (stats)
│   │   └── public.py              # /api/public/* (services без JWT)
│   ├── schemas/                   # Pydantic схемы
│   ├── api/                       # Дополнительные API-модули
│   ├── services/                  # Бизнес-логика
│   └── db/                        # Миграции БД
├── nginx/
│   ├── nginx.conf                 # Основной конфиг (server_tokens off)
│   └── conf.d/crm.conf            # HTTP→HTTPS, rate-limit, security headers
├── scripts/
│   ├── migrate_and_seed.py        # Создание leads колонок + 10 услуг
│   ├── migrate_applications.py    # applications + 10 тестовых заявок
│   ├── migrate_metrics.py         # behavior_metrics миграция
│   └── migrate_notes.py           # notes колонка в applications
├── docker-compose.yml             # postgres, nginx, backend, watchtower
├── .env                           # Переменные окружения
├── Dockerfile
└── requirements.txt
```

## Модели данных

| Модель | Таблица | Ключевые поля |
|--------|---------|---------------|
| LeadModel | leads | first_name, last_name, contact_data, budget, priority, status, planned_start/end, assigned_to, estimated/actual_cost, payment_status |
| BehaviorModel | behaviors | lead_id (FK), time_spent_seconds, buttons_clicked, scroll_depth, device_type, browser, utm_* |
| AdminUserModel | admin_users | username (UNIQUE), password_hash (bcrypt), is_active |
| AdminDataModel | admin_data | service_name, budget_range, available_products, form_settings, ui_config |
| AdminSettingModel | admin_settings | service_name, budget_range, task_type, product_interest, description |
| ApplicationModel | applications | Все поля Lead + status, notes, scoring (runtime) |
| BehaviorMetricModel | behavior_metrics | application_id, time_on_page, buttons_clicked, cursor_positions (INSERT-only) |

## Система скоринга

`app/core/scoring.py` — `calculate_lead_score(application_dict)`:

- **8 критериев** (бюджет 25, размер компании 20, дедлайн 15, роль 10, объём 10, ниша 10, контакты 5, комментарий 5)
- **Макс. 100 баллов**
- **Температура:** hot (≥70), warm (40–69), cold (<40)
- **Рекомендация отдела:** по нише бизнеса + типу задачи
- **Инсайты:** автоматические текстовые рекомендации
- **Персональный менеджер:** если score ≥ 60 или руководитель

## Быстрый старт

```bash
# Запуск
docker compose up -d --build

# Проверка
docker ps
curl -k https://localhost/health

# Пересборка при изменении Python-файлов
docker compose build --no-cache backend && docker compose up -d
```

## API Endpoints

| Префикс | Эндпоинты | JWT |
|---------|-----------|-----|
| `/api/auth/*` | register, login, refresh, check, me | — (кроме me) |
| `/api/leads/*` | CRUD лидов | — (только POST) |
| `/api/behaviors/*` | CRUD поведений | — (только POST) |
| `/api/behavior-metrics/*` | CRUD + stats метрик | — (только POST) |
| `/api/applications/*` | CRUD + scored + stats | — (только POST) |
| `/api/admin/*` | CRUD AdminData | Да |
| `/api/admin/services/*` | CRUD услуг | Да |
| `/api/public/*` | services (active only) | — |
| `/health` | Health check | — |

Полная документация: [API_DOCS.md](API_DOCS.md)

## Безопасность

- Backend изолирован в Docker-сети `internal`
- JWT: access (30 мин) + refresh (7 дней), HS256
- CORS: только `https://orderscrm.ru`
- Swagger: `DISABLE_DOCS=true` отключает /docs, /openapi.json, /redoc
- Rate-limit: 10 req/s на `/api/`
- Регистрация блокируется после создания 1-го админа
