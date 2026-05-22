# API Документация — Orders CRM

Базовый URL: `https://orderscrm.ru` (production) / `http://localhost:8000` (локально)

---

## Аутентификация

### POST /api/auth/register

Регистрация первого администратора. Доступна только если админов ещё нет.

```json
// Request
{ "username": "admin", "password": "securepass123" }

// Response 201
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Ошибки:** `403` — админ уже существует; `400` — логин занят; `422` — валидация.

### POST /api/auth/login

Вход существующего администратора.

```json
// Request
{ "username": "admin", "password": "securepass123" }

// Response 200
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Ошибки:** `401` — неверный логин/пароль; `403` — учётная запись деактивирована.

### POST /api/auth/refresh

Обновление access-токена по refresh-токену.

```json
// Request
{ "refresh_token": "eyJhbGciOiJIUzI1NiIs..." }

// Response 200
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Ошибки:** `401` — невалидный токен или админ деактивирован.

### GET /api/auth/check

Проверка наличия администраторов.

```json
// Response 200
{ "has_admins": true, "count": 1 }
```

Используется фронтендом для показа формы входа или регистрации.

### GET /api/auth/me

Данные текущего администратора. **Требует JWT.**

```json
// Response 200
{
  "id": 1,
  "username": "admin",
  "created_at": "2026-05-22T10:00:00",
  "is_active": true
}
```

---

## Лиды (Leads)

### POST /api/leads/

Создать лид. Публичный эндпоинт. Автоматически создаёт запись в `applications`.

```json
// Request
{
  "first_name": "Иван",
  "last_name": "Петров",
  "middle_name": "Сергеевич",
  "contact_data": "+71234567890, ivan@example.com",
  "business_niche": "FinTech",
  "company_size": "50-200",
  "task_volume": "Большой",
  "role": "CEO",
  "business_info": "Финтех-стартап",
  "budget": "{\"min\": 500000, \"max\": 1000000}",
  "project_deadline": "2 месяца",
  "task_type": "Разработка",
  "product_interest": "Торговая платформа",
  "preferred_contact_method": "Телефон",
  "convenient_time": "10:00-18:00",
  "comment": "Нужна MVP платформа для торговли"
}

// Response 201
{
  "id": 1,
  "first_name": "Иван",
  "last_name": "Петров",
  ...
  "created_at": "2026-05-22T10:00:00",
  "updated_at": "2026-05-22T10:00:00"
}
```

### GET /api/leads/

Список лидов. **Требует JWT.**

`?skip=0&limit=100`

### GET /api/leads/{id}

Детали лида. **Требует JWT.**

### PUT /api/leads/{id}

Обновить лид. **Требует JWT.**

```json
// Request (частичное обновление)
{ "status": "В работе", "priority": "high" }
```

### DELETE /api/leads/{id}

Удалить лид. **Требует JWT.** `204 No Content`.

---

## Заявки (Applications / CRM)

### GET /api/applications/scored

Скорингованные заявки с температурой. **Требует JWT.**

```json
// Response 200
[
  {
    "id": 1,
    "first_name": "Анна",
    "last_name": "Смирнова",
    "budget": "{\"min\": 1000000, \"max\": 3000000}",
    "status": "Новая",
    "notes": null,
    "scoring": {
      "score": 90,
      "temperature": "hot",
      "temperature_label": "Горячий",
      "needs_personal_manager": true,
      "recommended_department": "FinTech-отдел",
      "score_breakdown": {
        "budget_score": 25,
        "company_size_score": 15,
        "deadline_score": 5,
        "role_score": 10,
        "task_volume_score": 10,
        "business_niche_score": 10,
        "contact_completeness_score": 5,
        "comment_score": 5
      },
      "insights": [
        "Высокий бюджет (1 000 000 руб) — приоритетная заявка",
        "Руководитель компании — принимает решения",
        "FinTech-сектор — высокая маржинальность",
        "Полные контактные данные — лёгкий выход на связь"
      ]
    }
  }
]
```

Сортировка: по убыванию `score`. `?skip=0&limit=100`

### GET /api/applications/stats

Статистика заявок. **Требует JWT.**

```json
// Response 200
{
  "total": 12,
  "hot_count": 3,
  "warm_count": 5,
  "cold_count": 4,
  "departments": [
    { "name": "AI-разработка", "count": 5 },
    { "name": "Общий отдел", "count": 3 },
    { "name": "FinTech-отдел", "count": 2 },
    { "name": "Backend-отдел", "count": 2 }
  ],
  "average_budget_max": 732916.67,
  "average_deadline_weeks": 4.5,
  "personal_manager_rate": 41.7
}
```

### GET /api/applications/{id}

Детали заявки со скорингом. **Требует JWT.**

### PUT /api/applications/{id}

Обновить заявку (статус, заметки). **Требует JWT.**

```json
// Request
{ "status": "В работе", "notes": "Перезвонить после 15:00" }
```

### DELETE /api/applications/{id}

Удалить заявку. **Требует JWT.** `204 No Content`.

---

## Поведенческие метрики (Behavior Metrics)

### POST /api/behavior-metrics/

Отправить метрику. Публичный эндпоинт (INSERT-only).

```json
// Request
{
  "application_id": 0,
  "time_on_page": 120,
  "buttons_clicked": "{\"hero_cta\": 2, \"submit_form\": 1}",
  "cursor_positions": "[{\"x\": 100, \"y\": 200}, {\"x\": 150, \"y\": 300}]",
  "return_frequency": 1
}

// Response 201
{ "id": 1, "application_id": 0, "time_on_page": 120, ... }
```

### GET /api/behavior-metrics/

Список метрик. **Требует JWT.** `?skip=0&limit=100`

### GET /api/behavior-metrics/stats

Агрегированная статистика. **Требует JWT.**

```json
// Response 200
{
  "avg_time_on_page": { "daily": 45, "weekly": 60, "monthly": 55 },
  "max_time_on_page": { "daily": 120, "weekly": 300, "monthly": 600 },
  "top_buttons": [
    { "button": "hero_cta", "clicks": 15 },
    { "button": "submit_form", "clicks": 8 }
  ],
  "heatmap_data": [
    { "x": 100, "y": 200, "frequency": 12 },
    { "x": 300, "y": 400, "frequency": 8 }
  ],
  "total_sessions": 5,
  "total_metrics_records": 120
}
```

---

## Поведение (Behaviors, 1:1 с Lead)

### POST /api/behaviors/

Создать поведение для лида. Публичный.

```json
// Request
{
  "lead_id": 1,
  "time_spent_seconds": 120.5,
  "buttons_clicked": "{\"submit\": 1}",
  "cursor_hover_zones": "...",
  "return_count": 0,
  "page_views": 3,
  "scroll_depth_percent": 75.0,
  "device_type": "desktop",
  "browser": "Chrome",
  "os": "Windows",
  "screen_resolution": "1920x1080",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "referrer": "https://google.com",
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "brand"
}
```

**Эндпоинты:** `GET /api/behaviors/`, `GET /api/behaviors/{lead_id}`, `PUT /api/behaviors/{lead_id}`, `DELETE /api/behaviors/{lead_id}` (все JWT, кроме POST).

---

## Admin Data (настройки фронтенда)

### GET /api/admin/active

Текущий активный конфиг. **Требует JWT.**

```json
// Response 200
{
  "id": 1,
  "service_name": "Разработка, Консультации",
  "budget_range": "{\"min\": 50000, \"max\": 5000000, \"step\": 50000}",
  "available_products": "MVP, Web, Bot, AI, FinTech",
  "contact_methods": "Телефон, Telegram, Email",
  "form_settings": "{\"show_middle_name\": true}",
  "ui_config": "{\"theme\": \"light\"}",
  "is_active": true
}
```

**Эндпоинты:** `POST /api/admin/`, `GET /api/admin/`, `GET /api/admin/{id}`, `PUT /api/admin/{id}`, `DELETE /api/admin/{id}` — все JWT.

---

## Услуги (Admin Settings / CRUD)

### GET /api/admin/services

Список всех услуг. **Требует JWT.**

```json
// Response 200
[
  {
    "id": 1,
    "service_name": "Разработка MVP",
    "budget_range": "{\"min\": 100000, \"max\": 1000000}",
    "task_type": "Разработка",
    "product_interest": "Торговая платформа",
    "description": "MVP под ключ",
    "is_active": true
  }
]
```

### POST /api/admin/services

Создать услугу. **Требует JWT.**

```json
// Request
{
  "service_name": "Новая услуга",
  "budget_range": "{\"min\": 50000, \"max\": 500000}",
  "task_type": "Разработка",
  "product_interest": "AI-агент",
  "description": "Описание услуги",
  "is_active": true
}
```

### GET /api/admin/services/{id}
### PUT /api/admin/services/{id}
### DELETE /api/admin/services/{id}

**Ошибки:** `404` — не найдено; `422` — валидация.

---

## Публичные

### GET /api/public/services

Активные услуги (без авторизации, для клиентского лендинга).

```json
// Response 200
[
  {
    "id": 1,
    "service_name": "Разработка MVP",
    "task_type": "Разработка",
    "product_interest": "Торговая платформа",
    "description": "MVP под ключ",
    "is_active": true
  }
]
```

Возвращает только услуги с `is_active=true`.

---

## Health

### GET /health

```json
// Response 200
{ "status": "healthy" }
```
