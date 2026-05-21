# Orders CRM Backend

## Архитектура системы

### C4 Level 1 - Context Diagram

```mermaid
graph TB
    User["👤 Пользователь<br/>(Тёплый клиент)"] -->|Заполняет форму| Frontend["🌐 Frontend<br/>(orderscrm.ru)"]
    Frontend -->|HTTP API| Nginx[" Nginx<br/>(Reverse Proxy)"]
    Nginx -->|Проксирует| Backend["⚙️ Backend<br/>(FastAPI)"]
    Backend -->|SQL| Postgres["🗄️ PostgreSQL<br/>(crm_db)"]
    Admin["👨‍ Администратор"] -->|Управление| pgAdmin["📊 pgAdmin<br/>(Web UI)"]
    pgAdmin -->|SQL| Postgres
    DevOps[" DevOps"] -->|docker login| Registry["📦 Docker Registry<br/>(порт 8080)"]
    Registry -->|Хранит образы| Backend
    
    style Nginx fill:#4CAF50,color:#fff
    style Backend fill:#2196F3,color:#fff
    style Postgres fill:#FF9800,color:#fff
    style pgAdmin fill:#9C27B0,color:#fff
    style Registry fill:#607D8B,color:#fff
```

### C4 Level 2 - Container Diagram

```mermaid
graph TB
    subgraph "Сервер 185.87.48.13"
        subgraph "Docker Network: crm_network"
            Nginx["🔒 Nginx<br/>nginx:alpine<br/>Порты: 80, 443"]
            Backend["⚙️ Backend<br/>FastAPI<br/>Порт: 8000 (внутр.)"]
            Postgres["️ PostgreSQL<br/>postgres:16-alpine<br/>Порт: 5432 (внутр.)"]
            pgAdmin["📊 pgAdmin<br/>dpage/pgadmin4<br/>Порт: 5050"]
            Registry["📦 Docker Registry<br/>registry:2<br/>Порт: 8080"]
        end
    end
    
    Internet[" Интернет"] -->|HTTP/HTTPS| Nginx
    Internet -->|HTTPS| pgAdmin
    Internet -->|HTTPS| Registry
    
    Nginx -->|Прокси| Backend
    Backend -->|SQL| Postgres
    pgAdmin -->|SQL| Postgres
    
    style Nginx fill:#4CAF50,color:#fff
    style Backend fill:#2196F3,color:#fff
    style Postgres fill:#FF9800,color:#fff
    style pgAdmin fill:#9C27B0,color:#fff
    style Registry fill:#607D8B,color:#fff
```

### UML - ER Diagram

```mermaid
erDiagram
    LEADS {
        int id PK
        varchar first_name
        varchar last_name
        varchar middle_name
        text contact_data
        varchar business_niche
        varchar company_size
        varchar task_volume
        varchar role
        text business_info
        varchar budget
        varchar project_deadline
        varchar task_type
        varchar product_interest
        varchar preferred_contact_method
        varchar convenient_time
        text comment
        timestamp created_at
        timestamp updated_at
    }
    
    BEHAVIORS {
        int lead_id PK,FK
        float time_spent_seconds
        text buttons_clicked
        text cursor_hover_zones
        int return_count
        int page_views
        float scroll_depth_percent
        varchar device_type
        varchar browser
        varchar os
        varchar screen_resolution
        varchar ip_address
        text user_agent
        varchar referrer
        varchar utm_source
        varchar utm_medium
        varchar utm_campaign
        timestamp created_at
        timestamp updated_at
    }
    
    ADMIN_DATA {
        int id PK
        text service_name
        text budget_range
        text available_products
        text contact_methods
        jsonb form_settings
        jsonb ui_config
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    
    LEADS ||--|| BEHAVIORS : "1-to-1"
```

### UML - Sequence Diagram (Создание лида)

```mermaid
sequenceDiagram
    participant C as Клиент (Браузер)
    participant N as Nginx
    participant B as Backend (FastAPI)
    participant D as PostgreSQL

    C->>N: POST /api/leads (JSON данные)
    N->>B: Проксирует запрос
    B->>B: Валидация (Pydantic)
    B->>D: INSERT INTO leads (...)
    D-->>B: RETURNING id
    B-->>N: 201 Created {id, first_name, ...}
    N-->>C: JSON ответ
    
    C->>N: POST /api/behaviors (метрики)
    N->>B: Проксирует запрос
    B->>D: INSERT INTO behaviors (lead_id, ...)
    D-->>B: OK
    B-->>N: 201 Created
    N-->>C: JSON ответ
```

## Структура проекта

```
backend/
├── app/
│   ├── main.py              # Точка входа, роутер
│   ├── core/
│   │   └── database.py      # Подключение к PostgreSQL
│   ├── models/
│   │   ├── lead.py          # Lead модель + CRUD
│   │   ├── behavior.py      # Behavior модель + CRUD
│   │   └── admin.py         # AdminData модель + CRUD
│   └── routes/
│       ├── lead.py          # Роуты /api/leads
│       ├── behavior.py      # Роуты /api/behaviors
│       └── admin.py         # Роуты /api/admin
├── db/
│   └── init.sql             # Инициализация БД
├── nginx/
│   ├── nginx.conf
│   └── conf.d/crm.conf      # Прокси на backend
├── registry/
│   └── auth/registry.htpasswd
── docker-compose.yml
├── .env
├── Dockerfile
└── requirements.txt
```

## API Endpoints

### Leads

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/leads/` | Создать лид |
| GET | `/api/leads/` | Список лидов |
| GET | `/api/leads/{id}` | Получить лид |
| PUT | `/api/leads/{id}` | Обновить лид |
| DELETE | `/api/leads/{id}` | Удалить лид |

### Behaviors

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/behaviors/` | Создать поведение |
| GET | `/api/behaviors/` | Список поведений |
| GET | `/api/behaviors/{lead_id}` | Получить поведение |
| PUT | `/api/behaviors/{lead_id}` | Обновить поведение |
| DELETE | `/api/behaviors/{lead_id}` | Удалить поведение |

### Admin

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/admin/` | Создать конфиг |
| GET | `/api/admin/` | Список конфигов |
| GET | `/api/admin/active` | Активный конфиг |
| GET | `/api/admin/{id}` | Получить конфиг |
| PUT | `/api/admin/{id}` | Обновить конфиг |
| DELETE | `/api/admin/{id}` | Удалить конфиг |

### Health

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | Проверка статуса |

## Быстрый старт

### 1. Запуск

```bash
cd backend
docker compose up -d --build
```

### 2. Проверка

```bash
docker ps
curl http://185.87.48.13/health
```

### 3. Доступ к сервисам

| Сервис | URL | Логин | Пароль |
|--------|-----|-------|--------|
| Сайт | http://185.87.48.13 | - | - |
| pgAdmin | http://185.87.48.13:5050 | admin@orderscrm.ru | admin123 |
| Registry | http://185.87.48.13:8080 | admin | crm_password |
| PostgreSQL | 185.87.48.13:5432 | crm_user | crm_password |

## Безопасность

- Backend недоступен напрямую извне
- Все запросы проходят через Nginx
- PostgreSQL доступен только внутри сети
- Данные не покидают сервер

## Registry

```bash
# Логин
docker login 185.87.48.13:8080

# Пуш образа
docker tag orders-crm-backend:latest 185.87.48.13:8080/orders-crm-backend:latest
docker push 185.87.48.13:8080/orders-crm-backend:latest
```
