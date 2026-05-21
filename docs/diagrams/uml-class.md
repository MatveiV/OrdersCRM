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

    class LeadCreate {
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
    }

    class LeadResponse {
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
        +str created_at
        +str updated_at
    }

    class BehaviorCreate {
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
    }

    class AdminDataCreate {
        +str service_name
        +str budget_range
        +str available_products
        +str contact_methods
        +json form_settings
        +json ui_config
        +bool is_active
    }

    class LeadCRUD {
        +create(db, lead) LeadModel
        +get(db, lead_id) LeadModel
        +get_all(db, skip, limit) List[LeadModel]
        +update(db, lead_id, lead) LeadModel
        +delete(db, lead_id) bool
    }

    class BehaviorCRUD {
        +create(db, behavior) BehaviorModel
        +get(db, lead_id) BehaviorModel
        +get_all(db, skip, limit) List[BehaviorModel]
        +update(db, lead_id, behavior) BehaviorModel
        +delete(db, lead_id) bool
    }

    class AdminCRUD {
        +create(db, data) AdminDataModel
        +get(db, id) AdminDataModel
        +get_all(db, skip, limit) List[AdminDataModel]
        +get_active(db) AdminDataModel
        +update(db, id, data) AdminDataModel
        +delete(db, id) bool
    }

    LeadModel "1" --> "1" BehaviorModel : 1-to-1
    LeadCRUD ..> LeadModel : manages
    BehaviorCRUD ..> BehaviorModel : manages
    AdminCRUD ..> AdminDataModel : manages
    LeadCreate ..> LeadModel : creates
    LeadResponse ..> LeadModel : represents
    BehaviorCreate ..> BehaviorModel : creates
    AdminDataCreate ..> AdminDataModel : creates
```

## Описание классов

### Модели данных

| Класс | Файл | Назначение |
|-------|------|------------|
| LeadModel | app/models/lead.py | SQLAlchemy модель таблицы leads |
| BehaviorModel | app/models/behavior.py | SQLAlchemy модель таблицы behaviors |
| AdminDataModel | app/models/admin.py | SQLAlchemy модель таблицы admin_data |

### Pydantic схемы

| Класс | Файл | Назначение |
|-------|------|------------|
| LeadCreate | app/models/lead.py | Входная схема для создания лида |
| LeadResponse | app/models/lead.py | Выходная схема для ответа |
| BehaviorCreate | app/models/behavior.py | Входная схема для создания поведения |
| AdminDataCreate | app/models/admin.py | Входная схема для создания настроек |

### CRUD сервисы

| Класс | Файл | Назначение |
|-------|------|------------|
| LeadCRUD | app/models/lead.py | CRUD операции для лидов |
| BehaviorCRUD | app/models/behavior.py | CRUD операции для поведений |
| AdminCRUD | app/models/admin.py | CRUD операции для настроек |
