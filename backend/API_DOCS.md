# API админ-панели — Управление услугами

Базовый URL: `http://localhost:8000` (или из docker-compose)

Все эндпоинты требуют заголовок: `Authorization: Bearer <access_token>`

---

## GET /admin/services

Получить список всех услуг.

### Ответ (200 OK)

```json
[
  {
    "id": 1,
    "service_name": "Консультация",
    "budget_range": "{\"min\": 50000, \"max\": 500000, \"step\": 10000}",
    "task_type": "Аналитика",
    "product_interest": "AI-агент",
    "description": "Первичная консультация по проекту",
    "is_active": true,
    "created_at": "2025-01-15T10:30:00",
    "updated_at": "2025-01-20T14:00:00"
  }
]
```

**Важно:** Ответ всегда массив. Если услуг нет — `[]`.

---

## GET /admin/services/{id}

Получить услугу по ID.

### Ответ (200 OK)

Один объект услуги (см. выше).

### Ошибки

- `404 Not Found` — услуга не найдена

---

## POST /admin/services

Создать новую услугу.

### Тело запроса

```json
{
  "service_name": "Разработка MVP",
  "budget_range": "{\"min\": 100000, \"max\": 1000000, \"step\": 50000}",
  "task_type": "Разработка",
  "product_interest": "Торговая платформа",
  "description": "Разработка MVP под ключ",
  "is_active": true
}
```

### Ответ (201 Created)

Созданный объект услуги с id.

### Ошибки

- `422 Unprocessable Entity` — ошибка валидации (service_name пустой и т.д.)

---

## PUT /admin/services/{id}

Обновить услугу.

### Тело запроса

```json
{
  "service_name": "Новое название",
  "is_active": false
}
```

Можно передать только изменяемые поля.

### Ответ (200 OK)

Обновлённый объект услуги.

### Ошибки

- `404 Not Found`
- `422 Unprocessable Entity`

---

## DELETE /admin/services/{id}

Удалить услугу.

### Ответ (200 OK)

```json
{
  "success": true,
  "message": "Услуга удалена"
}
```

### Ошибки

- `404 Not Found`
