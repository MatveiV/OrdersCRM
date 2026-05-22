# UML Class Diagram — Backend Models

**Цель:** Показать классы моделей и их отношения

```mermaid
classDiagram
    class LeadModel {
        +int id
        +str first_name
        +str last_name
        +str middle_name
        +str contact_data
        +str business_niche
        +str company_size
        +str task_volume
        +str role
        +str business_info
        +str budget
        +str project_deadline
        +str task_type
        +str product_interest
        +str preferred_contact_method
        +str convenient_time
        +str comment
        +str priority
        +str status
        +str planned_start
        +str planned_end
        +str assigned_to
        +float estimated_cost
        +float actual_cost
        +str payment_status
        +str created_at
        +str updated_at
    }

    class BehaviorModel {
        +int lead_id
        +float time_spent_seconds
        +str buttons_clicked
        +str cursor_hover_zones
        +int return_count
        +int page_views
        +float scroll_depth_percent
        +str device_type
        +str browser
        +str os
        +str screen_resolution
        +str ip_address
        +str user_agent
        +str referrer
        +str utm_source
        +str utm_medium
        +str utm_campaign
        +str created_at
        +str updated_at
    }

    class AdminUserModel {
        +int id
        +str username
        +str password_hash
        +bool is_active
        +str created_at
    }

    class AdminDataModel {
        +int id
        +str service_name
        +str budget_range
        +str available_products
        +str contact_methods
        +json form_settings
        +json ui_config
        +bool is_active
        +str created_at
        +str updated_at
    }

    class AdminSettingModel {
        +int id
        +str service_name
        +str budget_range
        +str task_type
        +str product_interest
        +str description
        +bool is_active
        +str created_at
        +str updated_at
    }

    class ApplicationModel {
        +int id
        +str first_name
        +str last_name
        +str middle_name
        +str contact_data
        +str business_niche
        +str company_size
        +str task_volume
        +str role
        +str business_info
        +str budget
        +str project_deadline
        +str task_type
        +str product_interest
        +str preferred_contact_method
        +str convenient_time
        +str comment
        +str status
        +str notes
        +str created_at
        +dict scoring
    }

    class BehaviorMetricModel {
        +int id
        +int application_id
        +int time_on_page
        +str buttons_clicked
        +str cursor_positions
        +int return_frequency
        +datetime created_at
    }

    class ScoringEngine {
        +calculate_lead_score(application) dict
        +parse_budget(str) float
        +parse_deadline_weeks(str) float
    }

    class SecurityEngine {
        +hash_password(str) str
        +verify_password(str, str) bool
        +create_access_token(dict) str
        +create_refresh_token(dict) str
        +decode_token(str) dict
        +get_current_admin(token) AdminUserModel
    }

    LeadModel "1" --> "1" BehaviorModel : 1-to-1
    LeadModel "1" ..> "0..1" ApplicationModel : auto-creates
    ApplicationModel ..> ScoringEngine : uses for scoring
    SecurityEngine ..> AdminUserModel : verifies JWT

    note for ScorigngEngine "8 criteria, max 100 pts\nhot >= 70, warm >= 40\ncold < 40\n+ insights + department"
    note for SecurityEngine "JWT HS256\naccess 30min\nrefresh 7 days\nbcrypt passwords"
```

## Описание классов

### Модели данных (SQLAlchemy)

| Класс | Таблица | Файл | Назначение |
|-------|---------|------|------------|
| LeadModel | leads | app/models/lead.py | Сырые заявки + поля планирования/стоимости |
| BehaviorModel | behaviors | app/models/behavior.py | Поведение (1:1 с Lead) |
| AdminUserModel | admin_users | app/models/admin_user.py | Администраторы (bcrypt, JWT) |
| AdminDataModel | admin_data | app/models/admin.py | Настройки фронтенда |
| AdminSettingModel | admin_settings | app/models/admin_settings.py | Услуги компании |
| ApplicationModel | applications | app/models/application.py | Заявки CRM (со скорингом runtime) |
| BehaviorMetricModel | behavior_metrics | app/models/behavior_metric.py | Анонимные метрики (INSERT-only) |

### Core-модули

| Класс | Файл | Назначение |
|-------|------|------------|
| ScorigngEngine | app/core/scoring.py | 8 критериев скоринга, 100 баллов |
| SecurityEngine | app/core/security.py | JWT (HS256), bcrypt, get_current_admin |
