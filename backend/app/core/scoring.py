import json
import re


def parse_budget(budget_str):
    if not budget_str:
        return 0
    try:
        data = json.loads(budget_str)
        values = []
        for k in ("max", "min"):
            if k in data:
                values.append(float(data[k]))
        if values:
            return max(values)
    except (json.JSONDecodeError, ValueError, TypeError):
        pass
    nums = re.findall(r"[\d ]+", budget_str.replace(" ", ""))
    for n in nums:
        try:
            return float(n)
        except ValueError:
            continue
    return 0


def parse_deadline_weeks(deadline_str):
    if not deadline_str:
        return 0
    s = deadline_str.lower()
    if "asap" in s or "вчера" in s or "сроч" in s:
        return 0.5
    nums = re.findall(r"\d+", s)
    if not nums:
        return 99
    n = int(nums[0])
    if "недел" in s or "week" in s:
        return n
    if "месяц" in s or "month" in s:
        return n * 4
    if "дн" in s or "day" in s:
        return n / 7
    if "год" in s or "year" in s:
        return n * 52
    return n


def calculate_lead_score(application):
    budget_val = parse_budget(application.get("budget") or "")
    company_size = (application.get("company_size") or "").lower()
    deadline = application.get("project_deadline") or ""
    role = (application.get("role") or "").lower()
    task_volume = (application.get("task_volume") or "").lower()
    business_niche = (application.get("business_niche") or "").lower()
    contact_data = application.get("contact_data") or ""
    comment = application.get("comment") or ""
    task_type = (application.get("task_type") or "").lower()

    # Budget score (max 25)
    if budget_val >= 1_000_000:
        budget_score = 25
    elif budget_val >= 500_000:
        budget_score = 20
    elif budget_val >= 100_000:
        budget_score = 15
    elif budget_val >= 50_000:
        budget_score = 10
    elif budget_val > 0:
        budget_score = 5
    else:
        budget_score = 0

    # Company size score (max 20)
    if any(k in company_size for k in ("500+", "крупн", "enterprise", "корпора")):
        company_size_score = 20
    elif any(k in company_size for k in ("50", "200", "средн")):
        company_size_score = 15
    elif any(k in company_size for k in ("10", "11", "мал", "небольш")):
        company_size_score = 10
    elif any(k in company_size for k in ("1", "микро", "стартап")):
        company_size_score = 5
    else:
        company_size_score = 0

    # Deadline score (max 15)
    dl_weeks = parse_deadline_weeks(deadline)
    if dl_weeks <= 1:
        deadline_score = 15
    elif dl_weeks <= 2:
        deadline_score = 12
    elif dl_weeks <= 4:
        deadline_score = 8
    elif dl_weeks <= 12:
        deadline_score = 5
    else:
        deadline_score = 0

    # Role score (max 10)
    if any(k in role for k in ("руководител", "ceo", "директор", "владел", "founder")):
        role_score = 10
    elif any(k in role for k in ("менеджер", "team lead", "тимлид", "senior")):
        role_score = 7
    elif any(k in role for k in ("сотрудник", "специалист", "разработчик", "junior")):
        role_score = 4
    else:
        role_score = 0

    # Task volume score (max 10)
    if any(k in task_volume for k in ("очень большой", "крупн", "больш", "high", "big")):
        task_volume_score = 10
    elif any(k in task_volume for k in ("средн", "medium", "normal")):
        task_volume_score = 6
    elif any(k in task_volume for k in ("мал", "small", "low", "ниже")):
        task_volume_score = 3
    else:
        task_volume_score = 0

    # Business niche score (max 10)
    if any(k in business_niche for k in ("fintech", "финтех", "банк", "страхован", "finance")):
        business_niche_score = 10
    elif any(k in business_niche for k in ("it", "айти", "телеком", "software", "tech")):
        business_niche_score = 8
    elif any(k in business_niche for k in ("ритейл", "e-com", "ecom", "retail", "торгов")):
        business_niche_score = 6
    elif business_niche:
        business_niche_score = 4
    else:
        business_niche_score = 0

    # Contact completeness score (max 5)
    has_phone = bool(re.search(r"[\+\d]{7,}", contact_data))
    has_email = bool(re.search(r"[^@\s]+@[^@\s]+\.[^@\s]+", contact_data))
    if has_phone and has_email:
        contact_completeness_score = 5
    elif has_phone or has_email:
        contact_completeness_score = 3
    elif contact_data.strip():
        contact_completeness_score = 1
    else:
        contact_completeness_score = 0

    # Comment score (max 5)
    comment_stripped = comment.strip()
    if len(comment_stripped) > 20:
        comment_score = 5
    elif len(comment_stripped) > 0:
        comment_score = 2
    else:
        comment_score = 0

    score = (
        budget_score + company_size_score + deadline_score + role_score
        + task_volume_score + business_niche_score
        + contact_completeness_score + comment_score
    )

    if score >= 70:
        temperature = "hot"
        temperature_label = "Горячий"
    elif score >= 40:
        temperature = "warm"
        temperature_label = "Тёплый"
    else:
        temperature = "cold"
        temperature_label = "Холодный"

    if score >= 60 or any(k in role for k in ("руководител", "ceo", "директор", "владел", "founder")):
        needs_personal_manager = True
    else:
        needs_personal_manager = False

    # Department recommendation
    if any(k in business_niche for k in ("fintech", "финтех", "банк", "страхован", "finance", "торгов")):
        recommended_department = "FinTech-отдел"
    elif any(k in (business_niche + " " + task_type) for k in ("ai", "llm", "бот", "агент", "chatgpt", "gpt", "claude")):
        recommended_department = "AI-разработка"
    elif any(k in (business_niche + " " + task_type) for k in ("инфраструктур", "backend", "бэкенд", "devops", "ci/cd")):
        recommended_department = "Backend-отдел"
    elif any(k in (business_niche + " " + task_type) for k in ("ml", "аналитик", "data", "etl")):
        recommended_department = "Data Science"
    else:
        recommended_department = "Общий отдел"

    # Insights
    insights = []
    if budget_val >= 1_000_000:
        insights.append(f"Высокий бюджет ({int(budget_val):,} ₽) — приоритетная заявка".replace(",", " "))
    elif budget_val >= 500_000:
        insights.append("Выше среднего бюджет — обратите внимание")
    if any(k in role for k in ("руководител", "ceo", "директор", "владел", "founder")):
        insights.append("Руководитель компании — принимает решения")
    if dl_weeks <= 2:
        insights.append(f"Срочный дедлайн ({deadline}) — требуется быстрая реакция")
    if company_size_score >= 15:
        insights.append("Крупная компания — высокий потенциал")
    if any(k in business_niche for k in ("fintech", "финтех", "банк")):
        insights.append("FinTech-сектор — высокая маржинальность")
    if has_phone and has_email:
        insights.append("Полные контактные данные — лёгкий выход на связь")
    if len(comment_stripped) > 50:
        insights.append("Развёрнутый комментарий — клиент заинтересован")
    if budget_val >= 500_000 and any(k in role for k in ("руководител", "ceo", "директор")):
        insights.append("Бюджет + полномочия — максимальный приоритет")

    return {
        "score": score,
        "temperature": temperature,
        "temperature_label": temperature_label,
        "needs_personal_manager": needs_personal_manager,
        "recommended_department": recommended_department,
        "score_breakdown": {
            "budget_score": budget_score,
            "company_size_score": company_size_score,
            "deadline_score": deadline_score,
            "role_score": role_score,
            "task_volume_score": task_volume_score,
            "business_niche_score": business_niche_score,
            "contact_completeness_score": contact_completeness_score,
            "comment_score": comment_score,
        },
        "insights": insights,
    }
