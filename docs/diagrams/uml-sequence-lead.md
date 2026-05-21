# UML Sequence Diagram — Lead Submission

**Цель:** Показать процесс отправки заявки клиентом

```mermaid
sequenceDiagram
    autonumber
    participant C as Клиент (Browser)
    participant F as Client Frontend
    participant N as Nginx
    participant B as Backend API
    participant D as PostgreSQL
    participant L as LocalStorage

    Note over C,L: 1. Загрузка страницы
    C->>F: Открывает https://185.87.48.13
    F->>F: initAnimatedBackground()
    F->>F: renderProjects()
    F->>N: GET /api/admin/active
    N->>B: Прокси /api/admin/active → backend:8000
    B->>D: SELECT * FROM admin_data WHERE is_active = TRUE
    D-->>B: AdminData (service_name, budget_range, products)
    B-->>N: 200 OK + JSON
    N-->>F: JSON
    F->>F: populateDynamicFields(adminData)
    F->>F: initScrollAnimations()

    Note over C,L: 2. Трекинг поведения
    C->>F: Кликает, скроллит, наводит курсор
    F->>F: BehaviorTracker: записывает события
    F->>L: Сохраняет return_count

    Note over C,L: 3. Заполнение формы
    C->>F: Заполняет поля формы
    F->>F: Валидация: first_name, last_name, contact_data
    F->>F: Обновление значений range-слайдеров

    Note over C,L: 4. Отправка заявки
    C->>F: Нажимает "Отправить заявку"
    F->>F: validateForm()
    F->>F: Собирает leadData из FormData
    F->>F: Собирает behaviorData из BehaviorTracker
    F->>F: payload = { ...leadData, ...behaviorData }
    F->>N: POST /api/leads/ (JSON)
    N->>B: Прокси POST → backend:8000/api/leads/
    B->>B: Pydantic: LeadCreate.model_validate(payload)
    Note over B: extra="ignore" — игнорирует поля трекинга
    B->>D: INSERT INTO leads (...) VALUES (...)
    D-->>B: RETURNING * (новый lead_id)
    B->>D: INSERT INTO behaviors (lead_id, time_spent_seconds, ...) VALUES (...)
    D-->>B: RETURNING *
    B-->>N: 201 Created + LeadResponse JSON
    N-->>F: 201 Created + JSON
    F->>F: form.style.display = 'none'
    F->>F: success-message.style.display = 'block'
    F-->>C: "Заявка отправлена!"

    Note over C,L: 5. Сохранение возврата
    C->>L: beforeunload: return_count++
```

## Этапы процесса

| # | Этап | Описание |
|---|------|----------|
| 1 | Загрузка страницы | Инициализация анимаций, проектов, загрузка AdminData |
| 2 | Трекинг поведения | Запись кликов, скролла, hover-зон, возвратов |
| 3 | Заполнение формы | Валидация обязательных полей, обновление слайдеров |
| 4 | Отправка заявки | POST /api/leads/ с lead + behavior данными |
| 5 | Сохранение возврата | Увеличение return_count в localStorage |

## Обработка ошибок

| Ошибка | Причина | Действие |
|--------|---------|----------|
| 422 Unprocessable Entity | Невалидные данные | Показать ошибку валидации |
| 500 Internal Server Error | Ошибка БД | Показать "Произошла ошибка" |
| Network Error | Нет соединения | Показать "Попробуйте позже" |
