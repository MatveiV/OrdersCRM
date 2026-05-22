# UML ER Diagram — Database Schema

**Цель:** Показать структуру базы данных и связи между таблицами

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
        varchar priority
        varchar status
        text planned_start
        text planned_end
        varchar assigned_to
        float estimated_cost
        float actual_cost
        varchar payment_status
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

    ADMIN_USERS {
        int id PK
        varchar username UK
        varchar password_hash
        boolean is_active
        timestamp created_at
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

    ADMIN_SETTINGS {
        int id PK
        varchar service_name
        text budget_range
        varchar task_type
        varchar product_interest
        text description
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    APPLICATIONS {
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
        varchar status
        text notes
        timestamp created_at
    }

    BEHAVIOR_METRICS {
        int id PK
        int application_id
        int time_on_page
        text buttons_clicked
        text cursor_positions
        int return_frequency
        timestamp created_at
    }

    LEADS ||--|| BEHAVIORS : "1-to-1"
    LEADS ||--o{ APPLICATIONS : "авто-создание"
```

## Описание таблиц

### LEADS

| Колонка | Тип | Описание |
|---------|-----|----------|
| id | SERIAL PK | Уникальный идентификатор |
| first_name | VARCHAR(255) | Имя клиента |
| last_name | VARCHAR(255) | Фамилия |
| contact_data | TEXT | Email/телефон |
| priority | VARCHAR | Приоритет (low/medium/high) |
| status | VARCHAR | Статус (Новая/В работе/Архив) |
| planned_start/end | TEXT | Планируемые даты |
| assigned_to | VARCHAR | Ответственный |
| estimated/actual_cost | FLOAT | Смета/факт |
| payment_status | VARCHAR | Статус оплаты |

### BEHAVIORS

1:1 связь с LEADS по lead_id.

### ADMIN_USERS

| Колонка | Тип | Описание |
|---------|-----|----------|
| username | VARCHAR(255) UK | Логин администратора |
| password_hash | VARCHAR(255) | bcrypt хеш |
| is_active | BOOLEAN | Активен |

### ADMIN_DATA

Настройки для клиентского фронтенда.

### ADMIN_SETTINGS

Услуги компании (CRUD через админ-панель).

### APPLICATIONS

Структурированные заявки для CRM. Авто-создаются при POST /api/leads/.
Поле `scoring` — runtime (не хранится в БД).

### BEHAVIOR_METRICS

Анонимные метрики, INSERT-only, без FK.

## Индексы

| Таблица | Индекс | Колонка |
|---------|--------|---------|
| leads | idx_leads_created_at | created_at DESC |
| leads | idx_leads_last_name | last_name |
| behaviors | idx_behaviors_lead_id | lead_id |
| admin_settings | idx_admin_settings_service_name | service_name |
| behavior_metrics | idx_metrics_created_at | created_at DESC |
| applications | idx_applications_status | status |
