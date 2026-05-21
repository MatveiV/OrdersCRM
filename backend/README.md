# Orders CRM Backend

## Архитектура системы

### C4 Level 1 - Context Diagram

```mermaid
graph TB
    User["👤 Пользователь<br/>(Тёплый клиент)"] -->|Заполняет форму| Frontend["🌐 Frontend<br/>(orderscrm.ru)"]
    Frontend -->|HTTP API| Nginx[" Nginx<br/>(Reverse Proxy)"]
    Nginx -->|Проксирует| Backend["⚙️ Backend<br/>(FastAPI)"]
    Backend -->|SQL| Postgres["🗄️ PostgreSQL<br/>(crm_db)"]
    Admin["‍💼 Администратор"] -->|Управление| pgAdmin["📊 pgAdmin<br/>(Web UI)"]
    pgAdmin -->|SQL| Postgres
    DevOps["🔧 DevOps"] -->|docker login| Registry[" Docker Registry<br/>(порт 8080)"]
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
            Nginx[" Nginx<br/>nginx:alpine<br/>Порты: 80, 443"]
            Backend["️ Backend<br/>FastAPI<br/>Порт: 8000 (внутр.)"]
            Postgres["🗄️ PostgreSQL<br/>postgres:16-alpine<br/>Порт: 5432 (внутр.)"]
            pgAdmin[" pgAdmin<br/>dpage/pgadmin4<br/>Порт: 5050"]
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

### C4 Level 3 - Component Diagram (Backend)

```mermaid
graph TB
    subgraph "Backend (FastAPI)"
        API[" API Endpoints<br/>/api/leads<br/>/health"]
        Models["📋 Pydantic Models<br/>LeadCreate<br/>LeadResponse"]
        DB["🗄️ Database Layer<br/>asyncpg Pool"]
        Security["🔐 Security<br/>CORS Middleware<br/>IP Filtering"]
    end
    
    Nginx["🔒 Nginx"] -->|HTTP| API
    API -->|Валидация| Models
    API -->|SQL запросы| DB
    API -->|Проверка| Security
    DB -->|SQL| Postgres["🗄️ PostgreSQL"]
    
    style API fill:#2196F3,color:#fff
    style Models fill:#FF9800,color:#fff
    style DB fill:#4CAF50,color:#fff
    style Security fill:#F44336,color:#fff
```

### UML - Sequence Diagram (Создание лида)

```mermaid
sequenceDiagram
    participant C as Клиент (Браузер)
    participant N as Nginx
    participant B as Backend (FastAPI)
    participant D as PostgreSQL
    participant P as pgAdmin

    C->>N: POST /api/leads (JSON данные)
    N->>B: Проксирует запрос
    B->>B: Валидация данных (Pydantic)
    B->>B: Сбор метрик (IP, User-Agent)
    B->>D: INSERT INTO leads (...)
    D-->>B: RETURNING id, created_at
    B-->>N: 200 OK {id, created_at, contact_name}
    N-->>C: JSON ответ
    
    Note over P,D: Администратор<br/>просматривает лиды<br/>через pgAdmin
    P->>D: SELECT * FROM leads
    D-->>P: Данные лидов
```

### UML - ER Diagram (База данных)

```mermaid
erDiagram
    LEADS {
        int id PK
        timestamp created_at
        timestamp updated_at
        varchar contact_name
        varchar contact_phone
        varchar contact_email
        text business_info
        varchar budget
        varchar contact_method
        text comments
        jsonb lead_metrics
        jsonb technical_info
        text source_url
        varchar utm_source
        varchar utm_medium
        varchar utm_campaign
        inet ip_address
        text user_agent
        varchar status
        boolean processed
    }
    
    LEAD_SOURCES {
        int id PK
        varchar source_name
        timestamp created_at
    }
    
    AUDIT_LOG {
        int id PK
        timestamp created_at
        varchar table_name
        int record_id
        varchar action
        jsonb old_data
        jsonb new_data
        varchar changed_by
    }
    
    LEADS ||--o{ AUDIT_LOG : "tracked_by"
    LEAD_SOURCES ||--o{ LEADS : "referenced_by"
```

### UML - Class Diagram (Backend Models)

```mermaid
classDiagram
    class LeadCreate {
        +str contact_name
        +str contact_phone
        +EmailStr contact_email
        +str business_info
        +str budget
        +str contact_method
        +str comments
        +dict lead_metrics
        +dict technical_info
        +str source_url
        +str utm_source
        +str utm_medium
        +str utm_campaign
    }
    
    class LeadResponse {
        +int id
        +datetime created_at
        +str contact_name
    }
    
    class LeadModel {
        +int id
        +datetime created_at
        +datetime updated_at
        +str contact_name
        +str contact_phone
        +str contact_email
        +str business_info
        +str budget
        +str contact_method
        +str comments
        +dict lead_metrics
        +dict technical_info
        +str source_url
        +str utm_source
        +str utm_medium
        +str utm_campaign
        +str ip_address
        +str user_agent
        +str status
        +bool processed
    }
    
    class DatabaseService {
        +Pool pool
        +async create_pool()
        +async execute_query()
        +async fetch_lead()
    }
    
    LeadCreate --> LeadModel : "creates"
    LeadModel --> LeadResponse : "returns"
    DatabaseService --> LeadModel : "manages"
```

## Компоненты системы

| Сервис | Образ | Порт | Описание |
|--------|-------|------|----------|
| **Nginx** | nginx:alpine | 80, 443 | Reverse proxy, статика, изоляция API |
| **PostgreSQL** | postgres:16-alpine | 5432 (внутр.) | База данных лидов |
| **pgAdmin** | dpage/pgadmin4:latest | 5050 | Web-интерфейс для управления БД |
| **Docker Registry** | registry:2 | 8080 | Локальный репозиторий образов |

## Быстрый старт

### 1. Подключение к серверу

```bash
# SSH подключение по ключу
ssh -i C:\Users\MV\.ssh\six root@185.87.48.13

# Или через алиас
ssh orderscrm
```

### 2. Проверка контейнеров

```bash
# Список запущенных контейнеров
docker ps

# С красивым форматированием
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

### 3. Доступ к сервисам

| Сервис | URL | Логин | Пароль |
|--------|-----|-------|--------|
| Сайт | http://185.87.48.13 | - | - |
| pgAdmin | http://185.87.48.13:5050 | admin@orderscrm.ru | admin123 |
| Registry | http://185.87.48.13:8080 | admin | crm_password |
| PostgreSQL | 185.87.48.13:5432 | crm_user | crm_password |

### 4. Работа с Registry

```bash
# Настройка insecure registry (Windows)
# Добавить в %USERPROFILE%\.docker\daemon.json:
{
  "insecure-registries": ["185.87.48.13:8080"]
}

# Перезапустить Docker Desktop

# Логин в registry
docker login 185.87.48.13:8080
# Username: admin
# Password: crm_password

# Пуш образа
docker tag my-backend:latest 185.87.48.13:8080/orders-crm-backend:latest
docker push 185.87.48.13:8080/orders-crm-backend:latest
```

## API Endpoints

### POST /api/leads

Создание нового лида (тёплый клиент).

**Request:**
```json
{
  "contact_name": "Иван Иванов",
  "contact_phone": "+79001234567",
  "contact_email": "ivan@example.com",
  "business_info": "Интернет-магазин одежды",
  "budget": "100000-200000",
  "contact_method": "phone",
  "comments": "Хочу CRM для управления заказами",
  "lead_metrics": {
    "form_fills": 3,
    "time_on_page": 120,
    "scroll_depth": 85
  },
  "technical_info": {
    "browser": "Chrome",
    "os": "Windows",
    "device": "desktop"
  },
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "summer_sale"
}
```

**Response:**
```json
{
  "id": 1,
  "created_at": "2026-05-21T12:00:00Z",
  "contact_name": "Иван Иванов"
}
```

### GET /health

Проверка состояния сервиса.

**Response:**
```json
{"status": "healthy"}
```

## Структура проекта

```
backend/
├── app/
│   ├── main.py          # FastAPI приложение
│   ├── api/             # API endpoints
│   ├── models/          # SQLAlchemy модели
│   ├── schemas/         # Pydantic схемы
│   └── services/        # Бизнес-логика
├── db/
│   └── init.sql         # Инициализация БД
├── nginx/
│   ├── nginx.conf       # Основная конфигурация
│   └── conf.d/
│       └── crm.conf     # Конфиг виртуальных хостов
├── registry/
│   ├── auth/
│   │   ── registry.htpasswd  # Файл авторизации
│   └── create-user.sh   # Скрипт создания пользователя
── docker-compose.yml   # Конфигурация сервисов
├── .env                 # Переменные окружения
├── Dockerfile           # Сборка backend
└── requirements.txt     # Python зависимости
```

## Безопасность

### Изоляция Backend
- Backend недоступен напрямую извне
- Все запросы проходят через Nginx
- Nginx проксирует только `/api/` на backend
- Директива `internal` блокирует внешний доступ

### Сеть
- Все сервисы в изолированной сети `crm_network`
- PostgreSQL доступен только внутри сети
- Открытые порты: 80, 443, 5050, 8080

### Данные
- Все данные хранятся локально
- Резервные копии в `postgres_data` volume
- Аудит изменений в `audit_log` таблице

## Мониторинг

```bash
# Логи всех сервисов
docker compose logs -f

# Логи конкретного сервиса
docker compose logs -f postgres

# Статистика ресурсов
docker stats

# Проверка здоровья PostgreSQL
docker compose exec postgres pg_isready -U crm_user -d crm_db
```

## Резервное копирование

```bash
# Бэкап базы данных
docker compose exec postgres pg_dump -U crm_user crm_db > backup.sql

# Восстановление
docker compose exec -T postgres psql -U crm_user crm_db < backup.sql
```

## Устранение проблем

### Не запускается PostgreSQL
```bash
docker compose logs postgres
docker compose restart postgres
```

### Нет доступа к pgAdmin
```bash
# Проверьте порт
netstat -tuln | grep 5050
```

### Ошибка подключения к Registry
```bash
# Проверьте htpasswd
cat registry/auth/registry.htpasswd
```

### Контейнер перезапускается
```bash
# Проверьте логи
docker logs <container_name>
```

## Следующие шаги

1. ✅ Создать структуру проекта
2. ✅ Настроить PostgreSQL
3. ✅ Настроить Nginx с изоляцией
4. ✅ Настроить Docker Registry
5. ⏳ Добавить Backend сервис в docker-compose
6. ⏳ Настроить SSL/TLS
7. ⏳ Настроить мониторинг
8. ⏳ Добавить CI/CD pipeline