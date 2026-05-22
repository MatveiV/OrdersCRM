# UML Sequence Diagram — Lead Submission

**Цель:** Показать процесс отправки заявки клиентом и последующей обработки

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
    C->>F: Открывает https://orderscrm.ru
    F->>F: initAnimatedBackground()
    F->>F: renderProjects()
    F->>F: initBehaviorTracking()
    F->>N: GET /api/admin/active
    N->>B: Прокси → backend:8000
    B->>D: SELECT * FROM admin_data WHERE is_active = TRUE
    D-->>B: AdminData (services, budget, products)
    B-->>N: 200 OK + JSON
    N-->>F: JSON
    F->>F: populateDynamicFields(adminData)
    F->>F: initScrollAnimations()

    Note over C,L: 2. Трекинг поведения (каждые 60с)
    C->>F: Кликает, скроллит, наводит курсор
    F->>F: behavior-metrics.js: запись в буфер
    F->>N: POST /api/behavior-metrics/ (time_on_page, buttons, cursor)
    N->>B: Прокси
    B->>D: INSERT INTO behavior_metrics
    D-->>B: OK
    B-->>N: 201 Created
    N-->>F: JSON

    Note over C,L: 3. Заполнение формы
    C->>F: Заполняет поля
    F->>F: Валидация first_name, last_name, contact_data
    F->>F: Обновление range-слайдеров

    Note over C,L: 4. Отправка заявки
    C->>F: Нажимает "Отправить заявку"
    F->>F: validateForm()
    F->>F: payload = { leadData, behaviorData }
    F->>N: POST /api/leads/ (JSON)
    N->>B: Прокси → backend:8000
    B->>B: Pydantic: LeadCreate.model_validate()
    B->>D: INSERT INTO leads (...) VALUES (...)
    D-->>B: RETURNING lead_id
    B->>B: ApplicationCreate из leadData
    B->>D: INSERT INTO applications (...) VALUES (...)
    D-->>B: RETURNING app_id
    B->>D: INSERT INTO behaviors (lead_id, ...)
    D-->>B: OK
    B-->>N: 201 Created + LeadResponse JSON
    N-->>F: JSON
    F->>F: Скрыть форму, показать "Заявка отправлена!"
    F-->>C: Сообщение об успехе

    Note over C,L: 5. Фоновая отправка метрик
    C->>L: beforeunload: sendBeacon()
    L->>N: navigator.sendBeacon (метрики)
    N->>B: POST /api/behavior-metrics/
    B->>D: INSERT INTO behavior_metrics
```

## Этапы процесса

| # | Этап | Описание |
|---|------|----------|
| 1 | Загрузка страницы | Инициализация анимаций, проектов, трекинга, загрузка AdminData |
| 2 | Фоновый трекинг | Каждые 60с: time_on_page, buttons, cursor_positions → behavior_metrics |
| 3 | Заполнение формы | Валидация полей, слайдеры |
| 4 | Отправка заявки | Lead → Application (авто) → Behavior → ответ |
| 5 | Закрытие страницы | sendBeacon с финальными метриками |

## Авто-создание Application

При создании Lead, бэкенд автоматически создаёт запись в `applications` с теми же данными. Это позволяет:
- Разделить сырые лиды (лендинг) и структурированные заявки (CRM)
- Применить скоринг к заявкам без изменения логики лендинга
- Вести независимый статус и заметки в CRM

## Обработка ошибок

| Ошибка | Причина | Действие |
|--------|---------|----------|
| 422 | Невалидные данные | Показать ошибку валидации |
| 500 | Ошибка БД | Показать "Произошла ошибка" |
| Network Error | Нет соединения | Показать "Попробуйте позже" |
