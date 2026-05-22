# Orders CRM — Документация

Премиальная CRM-система для управления заявками тёплых клиентов.

## Версии документации

| Версия | Дата | Описание |
|--------|------|----------|
| [v1.3](#v13-2026-05-22) | 2026-05-22 | JWT-авторизация админ-панели, CRUD услуг, frontend-admin SPA |
| [v1.2](#v12-2026-05-21) | 2026-05-21 | HTTPS, клиентский лендинг, админ-панель /admin, C4/UML диаграммы |
| [v1.1](#v11-2026-05-17) | 2026-05-17 | Добавлен фронтенд (Vite + Vanilla JS), Glassmorphism UI, трекинг поведения |
| [v1.0](#v10-2026-05-16) | 2026-05-16 | Инициализация проекта, базовая архитектура, FastAPI + PostgreSQL |

---

## v1.3 (2026-05-22)

### Что нового

- **JWT-авторизация** — регистрация первого администратора, вход/выход, access + refresh токены
- **Защита маршрутов** — все админские эндпоинты (кроме POST /leads и POST /behaviors) требуют `Bearer <token>`
- **CRUD услуг** — полноценное управление услугами (admin_settings) через админ-панель
- **frontend-admin/** — новое SPA-приложение на Vite с авторизацией, dashboard и CRUD-интерфейсом
- **API документация** — `backend/API_DOCS.md` с описанием эндпоинтов услуг

### Маршруты

| Маршрут | Описание | Защита |
|---------|----------|--------|
| `/` | Клиентский лендинг (Hero + Проекты + Форма) | — |
| `/admin` | Админ-панель (авторизация + dashboard + CRUD услуг) | JWT |
| `/api/auth/register` | Регистрация (только 1-й админ) | — |
| `/api/auth/login` | Вход, получение JWT | — |
| `/api/auth/refresh` | Обновление access-токена | — |
| `/api/auth/check` | Проверка наличия админов | — |
| `/api/auth/me` | Данные текущего админа | JWT |
| `/api/leads/` | CRUD лидов (POST — публичный) | JWT (GET/PUT/DELETE) |
| `/api/behaviors/` | CRUD поведений (POST — публичный) | JWT (GET/PUT/DELETE) |
| `/api/admin/` | CRUD AdminData | JWT |
| `/api/admin/services` | CRUD услуг (admin_settings) | JWT |
| `/docs` | Swagger UI | — |
| `/health` | Health check | — |

### Диаграммы

- [C4 Context Diagram](docs/diagrams/c4-context.md)
- [C4 Container Diagram](docs/diagrams/c4-container.md)
- [C4 Component Diagram](docs/diagrams/c4-component.md)
- [UML Sequence — Lead Submission](docs/diagrams/uml-sequence-lead.md)
- [UML Class Diagram](docs/diagrams/uml-class.md)
- [UML ER Diagram](docs/diagrams/uml-er.md)

---

## v1.2 (2026-05-21)

### Что нового

- **HTTPS** — самоподписанный SSL-сертификат, HTTP→HTTPS redirect, security headers
- **Клиентский лендинг** (`/`) — Hero-секция, портфолио проектов, форма заявки
- **Админ-панель** (`/admin`) — перенесена старая форма на отдельный маршрут
- **Дизайн-система** — светлая тема, Nunito/Nunito Sans/Comfortaa, золотые акценты
- **Портфолио** — 13 карточек проектов с фильтрацией по категориям
- **C4 и UML диаграммы** — полная визуализация архитектуры

---

## v1.1 (2026-05-17)

### Что нового

- **Фронтенд** — Vite + Vanilla JS, Glassmorphism UI
- **Трекинг поведения** — время на странице, клики, скролл, возвраты
- **Динамические формы** — загрузка настроек из AdminData
- **Анимации** — CSS + легковесный JS, золотые частицы
- **Docker Registry** — локальный реестр образов на порту 8080

### Фронтенд

- Сборка: `npm run build` → `dist/`
- Стили: Glassmorphism, тёмная тема, золотые акценты
- Шрифты: Cormorant Garamond + Inter
- Адаптивность: mobile, tablet, desktop

### Бэкенд

- Модели: Lead, Behavior (1:1), AdminData
- Async SQLAlchemy + asyncpg
- Pydantic валидация

---

## v1.0 (2026-05-16)

### Что нового

- **Инициализация проекта** — базовая структура
- **FastAPI бэкенд** — CRUD API для лидов
- **PostgreSQL 16** — основная БД
- **Docker Compose** — оркестрация сервисов
- **Nginx** — проксирование API, раздача статики
- **pgAdmin** — управление БД

### Архитектура

```mermaid
graph TB
    User["👤 Пользователь"] -->|HTTP/HTTPS| Nginx["🔒 Nginx<br/>Порты: 80, 443"]
    Nginx -->|Статика| Frontend["🎨 Frontend<br/>Vite + Vanilla JS"]
    Nginx -->|Прокси| Backend["⚙️ Backend<br/>FastAPI"]
    Backend -->|SQL| Postgres["🗄️ PostgreSQL<br/>crm_db"]
    Admin["👨‍💼 Админ"] -->|Управление| pgAdmin["📊 pgAdmin<br/>Порт: 5050"]
    pgAdmin -->|SQL| Postgres
    DevOps["🔧 DevOps"] -->|docker login| Registry["📦 Registry<br/>Порт: 8080"]
    
    style Nginx fill:#4CAF50,color:#fff
    style Frontend fill:#2196F3,color:#fff
    style Backend fill:#FF9800,color:#fff
    style Postgres fill:#9C27B0,color:#fff
    style pgAdmin fill:#607D8B,color:#fff
    style Registry fill:#795548,color:#fff
```

---

## Быстрый старт

### 1. Клонирование

```bash
git clone https://github.com/MatveiV/OrdersCRM.git
cd OrdersCRM
```

### 2. Запуск бэкенда

```bash
cd backend
docker compose up -d --build
```

### 3. Сборка фронтенда (клиентский лендинг)

```bash
cd frontend-client
npm install
npm run build
```

### 4. Сборка админ-панели

```bash
cd frontend-admin
npm install
npm run build
```

### 5. Деплой

```bash
# Копирование файлов на сервер
scp -r frontend-client/dist/* root@185.87.48.13:/tmp/
scp -r frontend-admin/dist/* root@185.87.48.13:/tmp/admin/

# Копирование в nginx контейнер
ssh root@185.87.48.13 "docker cp /tmp/. orderscrm_nginx:/usr/share/nginx/html/"
ssh root@185.87.48.13 "docker cp /tmp/admin/. orderscrm_nginx:/usr/share/nginx/html/admin/"
ssh root@185.87.48.13 "docker restart orderscrm_nginx"
```

## Доступ к сервисам

| Сервис | URL | Логин | Пароль |
|--------|-----|-------|--------|
| Лендинг | https://185.87.48.13 | — | — |
| Админ-панель | https://185.87.48.13/admin | (регистрация 1-го админа) | — |
| Swagger Docs | https://185.87.48.13/docs | — | — |
| pgAdmin | https://185.87.48.13:5050 | admin@orderscrm.ru | admin123 |
| Registry | https://185.87.48.13:8080 | admin | crm_password |
| PostgreSQL | 185.87.48.13:5432 | crm_user | crm_password |

## API Endpoints

### Authentication

| Метод | Путь | Описание | Защита |
|-------|------|----------|--------|
| POST | `/api/auth/register` | Регистрация первого администратора | — |
| POST | `/api/auth/login` | Вход, получение JWT токенов | — |
| POST | `/api/auth/refresh` | Обновление access-токена | — |
| GET | `/api/auth/check` | Проверка наличия админов | — |
| GET | `/api/auth/me` | Данные текущего администратора | JWT |

### Leads

| Метод | Путь | Описание | Защита |
|-------|------|----------|--------|
| POST | `/api/leads/` | Создать лид | — |
| GET | `/api/leads/` | Список лидов | JWT |
| GET | `/api/leads/{id}` | Получить лид | JWT |
| PUT | `/api/leads/{id}` | Обновить лид | JWT |
| DELETE | `/api/leads/{id}` | Удалить лид | JWT |

### Behaviors

| Метод | Путь | Описание | Защита |
|-------|------|----------|--------|
| POST | `/api/behaviors/` | Создать поведение | — |
| GET | `/api/behaviors/` | Список поведений | JWT |
| GET | `/api/behaviors/{lead_id}` | Получить поведение | JWT |
| PUT | `/api/behaviors/{lead_id}` | Обновить поведение | JWT |
| DELETE | `/api/behaviors/{lead_id}` | Удалить поведение | JWT |

### Admin Data

| Метод | Путь | Описание | Защита |
|-------|------|----------|--------|
| POST | `/api/admin/` | Создать конфиг | JWT |
| GET | `/api/admin/` | Список конфигов | JWT |
| GET | `/api/admin/active` | Активный конфиг | JWT |
| GET | `/api/admin/{id}` | Получить конфиг | JWT |
| PUT | `/api/admin/{id}` | Обновить конфиг | JWT |
| DELETE | `/api/admin/{id}` | Удалить конфиг | JWT |

### Admin Services

| Метод | Путь | Описание | Защита |
|-------|------|----------|--------|
| GET | `/api/admin/services` | Список услуг | JWT |
| POST | `/api/admin/services` | Создать услугу | JWT |
| GET | `/api/admin/services/{id}` | Получить услугу | JWT |
| PUT | `/api/admin/services/{id}` | Обновить услугу | JWT |
| DELETE | `/api/admin/services/{id}` | Удалить услугу | JWT |

### Health

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | Проверка статуса |

## Фронтенд

### Структура

| Директория | Назначение | Стек |
|-----------|-----------|------|
| `frontend-client/` | Клиентский лендинг (Hero, проекты, форма заявки) | Vite + Vanilla JS |
| `frontend-admin/` | Админ-панель (авторизация, dashboard, CRUD услуг) | Vite + Vanilla JS |
| `frontend/` | Устаревшая форма заявки (не используется) | Vite + Vanilla JS |

### Технологии

- **Сборка:** Vite
- **Стили:** Чистый CSS
- **Шрифты:** Nunito, Nunito Sans, Comfortaa (лендинг); Cormorant Garamond, Inter (админ)
- **Анимации:** CSS + легковесный JS
- **Авторизация:** JWT (localStorage), автоматическое обновление токенов

### Дизайн

- Лендинг: светлая тема, индиго (#1E3A5F), золото (#D4AF37)
- Админ-панель: спокойный светлый стиль (#F8F9FA), синие акценты (#4A6FA5)
- Страница входа: тёмная тема с золотыми акцентами
- Адаптивная вёрстка

### Функционал админ-панели

- JWT-авторизация (регистрация 1-го админа, вход, refresh)
- Dashboard с боковой навигацией
- CRUD управление услугами (таблица, модальное окно, подтверждение удаления)
- Toast-уведомления об успехе/ошибке
- Автообновление access-токена при истечении

### Команды

```bash
npm install      # Установка зависимостей
npm run dev      # Запуск dev-сервера
npm run build    # Сборка в dist/
npm run preview  # Предпросмотр сборки
```

## Бэкенд

### Технологии

- **Фреймворк:** FastAPI
- **База данных:** PostgreSQL 16
- **ORM:** SQLAlchemy (async + asyncpg)
- **Валидация:** Pydantic
- **Авторизация:** JWT (python-jose, HS256)
- **Хеширование:** bcrypt (passlib)

### Модели данных

**AdminUser** — учётные записи администраторов:
- id, username (UNIQUE), password_hash (bcrypt), created_at, is_active

**Lead** — основная заявка клиента:
- first_name, last_name, middle_name, contact_data
- business_niche, company_size, task_volume, role
- business_info, budget, project_deadline, task_type
- product_interest, preferred_contact_method, convenient_time, comment

**Behavior** — поведение пользователя (1-к-1 с Lead):
- lead_id (FK), time_spent_seconds, buttons_clicked
- cursor_hover_zones, return_count, page_views
- scroll_depth_percent, device_type, browser, os
- screen_resolution, ip_address, user_agent, referrer
- utm_source, utm_medium, utm_campaign

**AdminData** — настройки для фронтенда:
- service_name, budget_range, available_products
- contact_methods, form_settings, ui_config, is_active

**AdminSetting** — услуги компании (CRUD через админ-панель):
- service_name, budget_range (JSON), task_type
- product_interest, description, is_active

## Docker Registry

```bash
# Логин
docker login 185.87.48.13:8080
# Username: admin
# Password: crm_password

# Пуш образа
docker tag my-image:latest 185.87.48.13:8080/my-image:latest
docker push 185.87.48.13:8080/my-image:latest
```

## Безопасность

- Backend недоступен напрямую извне (только через Nginx)
- JWT-авторизация: access (30 мин) + refresh (7 дней) токены
- Пароли хешируются bcrypt
- Защищённые эндпоинты возвращают 401 без валидного токена
- Регистрация нового админа невозможна после создания первого
- PostgreSQL доступен только внутри Docker сети
- HTTPS с SSL-сертификатом
- Security headers (HSTS, X-Frame-Options, X-Content-Type-Options)

## Мониторинг

```bash
# Логи всех сервисов
docker compose logs -f

# Логи конкретного сервиса
docker compose logs -f backend

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

## Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|-----------|----------|----------------------|
| `DATABASE_URL` | Подключение к PostgreSQL | `postgresql+asyncpg://crm_user:crm_password@postgres:5432/crm_db` |
| `JWT_SECRET_KEY` | Секретный ключ для JWT | `orders-crm-super-secret-key-change-in-production-32chars` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни access-токена | `30` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Время жизни refresh-токена | `7` |
| `PGADMIN_DEFAULT_EMAIL` | Email для pgAdmin | `admin@orderscrm.ru` |
| `PGADMIN_DEFAULT_PASSWORD` | Пароль для pgAdmin | `admin123` |
