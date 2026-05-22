# Orders CRM

Премиальная CRM-система для управления заявками тёплых клиентов с интеллектуальным скорингом и сбором поведенческих метрик.

**Production:** https://orderscrm.ru (самоподписанный HTTPS)
**Сервер:** 185.87.48.13

---

## Архитектура

```mermaid
graph TB
    User["Пользователь"] -->|HTTPS| Nginx["Nginx<br/>80 / 443"]
    Nginx -->|Статика /| Client["Клиентский лендинг<br/>Vite + Vanilla JS"]
    Nginx -->|Статика /admin| Admin["Админ-панель SPA<br/>Vite + Vanilla JS"]
    Nginx -->|/api/*| Backend["Backend API<br/>FastAPI + Python 3.12"]
    Backend -->|asyncpg| Postgres["PostgreSQL 16<br/>crm_db"]
    Backend -->|JWT| AdminUser["admin_users"]
    
    subgraph "Docker Network: internal"
        Nginx
        Backend
        Postgres
        Watchtower["Watchtower<br/>Авто-обновление"]
    end

    style Nginx fill:#4CAF50,color:#fff
    style Client fill:#2196F3,color:#fff
    style Admin fill:#FF9800,color:#fff
    style Backend fill:#9C27B0,color:#fff
    style Postgres fill:#607D8B,color:#fff
```

## Быстрый старт

```bash
git clone https://github.com/MatveiV/OrdersCRM.git
cd OrdersCRM/backend

# Запуск бэкенда (PostgreSQL + Backend + Nginx + Watchtower)
docker compose up -d --build

# Сборка клиентского лендинга
cd ../frontend-client
npm install && npm run build

# Сборка админ-панели
cd ../frontend-admin
npm install && npm run build

# Деплой на production
scp -r frontend-client/dist/* root@185.87.48.13:/tmp/
scp -r frontend-admin/dist/* root@185.87.48.13:/tmp/admin/
ssh root@185.87.48.13 "docker cp /tmp/. orderscrm_nginx:/usr/share/nginx/html/ && docker cp /tmp/admin/. orderscrm_nginx:/usr/share/nginx/html/admin/ && docker restart orderscrm_nginx"
```

## Состав сервисов

| Сервис | Технология | Порты | Назначение |
|--------|-----------|-------|------------|
| Nginx | nginx:alpine | 80, 443 | Reverse proxy, SSL termination, статика, rate-limit |
| Backend | Python 3.12 + FastAPI | 8000 (внутр.) | REST API, бизнес-логика, скоринг |
| PostgreSQL | postgres:16-alpine | 5432 (внутр.) | Основная БД |
| Watchtower | containrrr/watchtower | — | Авто-обновление образов |

> pgAdmin и Docker Registry удалены из production конфигурации.

## Доступ к сервисам

| Сервис | URL |
|--------|-----|
| Клиентский лендинг | https://orderscrm.ru |
| Админ-панель | https://orderscrm.ru/admin |
| Health check | https://orderscrm.ru/health |
| Swagger | отключён в production (см. Безопасность) |

## Фронтенд

### Клиентский лендинг (`frontend-client/`)

Светлая тема, индиго (#1E3A5F) + золото (#D4AF37), шрифты Nunito/Comfortaa.

- Hero-секция с анимациями
- Портфолио проектов (13 карточек, фильтрация по категориям)
- Форма заявки с динамическими полями (из AdminData)
- **Сбор поведенческих метрик** — `behavior-metrics.js`: время на странице, клики (heatmap), скролл, возвраты
- Адаптивная вёрстка (mobile, tablet, desktop)

### Админ-панель (`frontend-admin/`)

Спокойный светлый стиль (#F8F9FA), синие акценты (#4A6FA5), шрифт Nunito.

- JWT-авторизация (страница входа, авто-refresh токенов)
- **Вкладка «Услуги»** — CRUD услуг компании (таблица + модалка + подтверждение удаления)
- **Вкладка «Заявки (лиды)»** — все заявки с лендинга с дополнительными полями (приоритет, статус, планирование, стоимость)
- **Вкладка «Заявки (CRM)»** — скорингованные заявки с температурой (hot/warm/cold), детальной модалкой (статусы, заметки, кнопка «Связаться»)
- **Вкладка «Статистика»** — агрегированные метрики поведения (среднее время, топ кнопок, heatmap)
- Toast-уведомления, модальные окна

## Бэкенд

### Технологии

| Компонент | Технология |
|-----------|-----------|
| Фреймворк | FastAPI (Python 3.12) |
| ORM | SQLAlchemy 2.0 (async + asyncpg) |
| Валидация | Pydantic v2 |
| Авторизация | JWT (python-jose, HS256) + bcrypt (passlib) |
| База данных | PostgreSQL 16 |

### Модели данных

| Модель | Таблица | Назначение |
|--------|---------|------------|
| `LeadModel` | `leads` | Сырые заявки с лендинга (с полями приоритета, планирования, стоимости) |
| `BehaviorModel` | `behaviors` | Поведение пользователя (1:1 с Lead) |
| `AdminUserModel` | `admin_users` | Учётные записи администраторов (bcrypt, JWT) |
| `AdminDataModel` | `admin_data` | Настройки фронтенда (список услуг, диапазоны, конфиг UI) |
| `AdminSettingModel` | `admin_settings` | Услуги компании (CRUD через админ-панель) |
| `ApplicationModel` | `applications` | Структурированные заявки для скоринга и CRM (авто-создание из Lead) |
| `BehaviorMetricModel` | `behavior_metrics` | Анонимные метрики поведения (INSERT-only, без FK) |

### Система скоринга

Модуль `backend/app/core/scoring.py` — `calculate_lead_score()`:

| Критерий | Макс. балл | Описание |
|----------|-----------|----------|
| Бюджет | 25 | >1M₽ → 25, >500K → 20, >100K → 15, >50K → 10 |
| Размер компании | 20 | Enterprise → 20, Средняя → 15, Малая → 10 |
| Дедлайн | 15 | ≤1 нед → 15, ≤2 нед → 12, ≤1 мес → 8 |
| Роль | 10 | Руководитель → 10, Менеджер → 7 |
| Объём задачи | 10 | Большой → 10, Средний → 6, Малый → 3 |
| Ниша бизнеса | 10 | FinTech → 10, IT → 8, Retail → 6 |
| Контакты | 5 | Телефон + Email → 5, Один → 3 |
| Комментарий | 5 | >20 символов → 5 |

**Температура:** hot (≥70), warm (40–69), cold (<40)
**Инсайты:** автоматические рекомендации по каждой заявке
**Рекомендация отдела:** AI-разработка, FinTech, Backend, Data Science, Общий отдел

### Эндпоинты API

#### Аутентификация

| Метод | Путь | Защита | Описание |
|-------|------|--------|----------|
| POST | `/api/auth/register` | — | Регистрация первого администратора |
| POST | `/api/auth/login` | — | Вход, получение JWT (access + refresh) |
| POST | `/api/auth/refresh` | — | Обновление access-токена |
| GET | `/api/auth/check` | — | Проверка наличия админов |
| GET | `/api/auth/me` | JWT | Данные текущего администратора |

#### Лиды (Leads)

| Метод | Путь | Защита | Описание |
|-------|------|--------|----------|
| POST | `/api/leads/` | — | Создать лид (авто-создание Application) |
| GET | `/api/leads/` | JWT | Список лидов |
| GET | `/api/leads/{id}` | JWT | Детали лида |
| PUT | `/api/leads/{id}` | JWT | Обновить лид |
| DELETE | `/api/leads/{id}` | JWT | Удалить лид |

#### Заявки (Applications / CRM)

| Метод | Путь | Защита | Описание |
|-------|------|--------|----------|
| POST | `/api/applications/` | — | Создать заявку |
| GET | `/api/applications/` | JWT | Список заявок |
| GET | `/api/applications/scored` | JWT | Скорингованные заявки (с температурой) |
| GET | `/api/applications/stats` | JWT | Статистика заявок |
| GET | `/api/applications/{id}` | JWT | Детали заявки (со скорингом) |
| PUT | `/api/applications/{id}` | JWT | Обновить заявку (статус, заметки) |
| DELETE | `/api/applications/{id}` | JWT | Удалить заявку |

#### Метрики поведения

| Метод | Путь | Защита | Описание |
|-------|------|--------|----------|
| POST | `/api/behavior-metrics/` | — | Отправить метрику (INSERT) |
| GET | `/api/behavior-metrics/` | JWT | Список метрик |
| GET | `/api/behavior-metrics/stats` | JWT | Агрегированная статистика |

#### Поведение (1:1 с Lead)

| Метод | Путь | Защита | Описание |
|-------|------|--------|----------|
| POST | `/api/behaviors/` | — | Создать поведение |
| GET | `/api/behaviors/` | JWT | Список поведений |
| GET | `/api/behaviors/{lead_id}` | JWT | Поведение по lead_id |
| PUT | `/api/behaviors/{lead_id}` | JWT | Обновить поведение |
| DELETE | `/api/behaviors/{lead_id}` | JWT | Удалить поведение |

#### Admin Data (настройки фронтенда)

| Метод | Путь | Защита | Описание |
|-------|------|--------|----------|
| POST | `/api/admin/` | JWT | Создать конфиг |
| GET | `/api/admin/` | JWT | Список конфигов |
| GET | `/api/admin/active` | JWT | Активный конфиг |
| GET | `/api/admin/{id}` | JWT | Детали конфига |
| PUT | `/api/admin/{id}` | JWT | Обновить конфиг |
| DELETE | `/api/admin/{id}` | JWT | Удалить конфиг |

#### Услуги (Admin Settings / CRUD)

| Метод | Путь | Защита | Описание |
|-------|------|--------|----------|
| GET | `/api/admin/services` | JWT | Список услуг |
| POST | `/api/admin/services` | JWT | Создать услугу |
| GET | `/api/admin/services/{id}` | JWT | Детали услуги |
| PUT | `/api/admin/services/{id}` | JWT | Обновить услугу |
| DELETE | `/api/admin/services/{id}` | JWT | Удалить услугу |

#### Публичные

| Метод | Путь | Защита | Описание |
|-------|------|--------|----------|
| GET | `/api/public/services` | — | Активные услуги (для лендинга) |

#### Health

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | `{"status": "healthy"}` |

### Поведенческие метрики

Клиентский скрипт `frontend-client/src/tracking/behavior-metrics.js`:

- Отправка каждые 60 секунд
- Трекинг: `time_on_page`, `buttons_clicked`, `cursor_positions` (heatmap), `return_frequency`
- `sendBeacon` при закрытии страницы
- Полностью анонимные, без FK-связей

**Статистика** (`GET /api/behavior-metrics/stats`):
- Среднее/макс время: daily, weekly, monthly
- Топ кнопок (агрегация JSON)
- Heatmap (Canvas, градиентные круги, 20px сетка)
- Общие счётчики

## Безопасность

| Мера | Описание |
|------|----------|
| Изоляция | Backend доступен только через Nginx (внутренняя сеть `internal`) |
| JWT | Access (30 мин) + Refresh (7 дней), HS256 |
| Пароли | bcrypt (passlib) |
| Регистрация | Только 1-й администратор (после — блокировка) |
| Swagger | Отключён (`DISABLE_DOCS=true`), заблокирован в nginx (403) |
| Rate-limit | 10 req/s на `/api/`, burst 20 |
| HTTPS | Самоподписанный сертификат, HSTS, security headers |
| Ports | Только 80, 443 открыты; 8000, 5432 — внутри Docker |
| CORS | Только `https://orderscrm.ru` |

## Мониторинг

```bash
# Логи
docker compose logs -f backend

# Статистика ресурсов
docker stats

# Проверка здоровья
curl https://orderscrm.ru/health

# Подключение к БД
docker compose exec postgres pg_isready -U crm_user -d crm_db

# Бэкап
docker compose exec postgres pg_dump -U crm_user crm_db > backup.sql
```

## Версии документации

| Версия | Дата | Описание |
|--------|------|----------|
| v2.0 | 2026-05-22 | Production: безопасность, скоринг, метрики, CRM, SPA-админка |
| v1.3 | 2026-05-22 | JWT-авторизация, CRUD услуг, frontend-admin SPA |
| v1.2 | 2026-05-21 | HTTPS, лендинг, админ-панель, диаграммы C4/UML |
| v1.1 | 2026-05-17 | Фронтенд (Vite + Vanilla JS), трекинг, Docker Registry |
| v1.0 | 2026-05-16 | Базовая архитектура: FastAPI + PostgreSQL + Nginx |

## Диаграммы

- [C4 Context Diagram](docs/diagrams/c4-context.md)
- [C4 Container Diagram](docs/diagrams/c4-container.md)
- [C4 Component Diagram](docs/diagrams/c4-component.md)
- [UML Sequence — Lead Submission](docs/diagrams/uml-sequence-lead.md)
- [UML Class Diagram](docs/diagrams/uml-class.md)
- [UML ER Diagram](docs/diagrams/uml-er.md)

## Переменные окружения

| Переменная | Описание | Production |
|-----------|----------|------------|
| `DATABASE_URL` | Подключение к PostgreSQL | `postgresql+asyncpg://crm_user:crm_password@postgres:5432/crm_db` |
| `JWT_SECRET_KEY` | Ключ подписи JWT | 32-символьный |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни access | 30 |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Время жизни refresh | 7 |
| `DISABLE_DOCS` | Отключить Swagger | `true` |
| `ENVIRONMENT` | Окружение | `production` |
| `CORS_ORIGINS` | Разрешённые CORS | `https://orderscrm.ru` |
| `NGINX_HTTP_PORT` | HTTP порт | 80 |
| `NGINX_HTTPS_PORT` | HTTPS порт | 443 |
