-- Orders CRM Database Initialization

-- Lead table
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    middle_name VARCHAR(255),
    contact_data TEXT,
    business_niche VARCHAR(255),
    company_size VARCHAR(100),
    task_volume VARCHAR(255),
    role VARCHAR(100),
    business_info TEXT,
    budget VARCHAR(100),
    project_deadline VARCHAR(255),
    task_type VARCHAR(255),
    product_interest VARCHAR(255),
    preferred_contact_method VARCHAR(100),
    convenient_time VARCHAR(100),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Behavior table (1-to-1 with leads)
CREATE TABLE IF NOT EXISTS behaviors (
    lead_id INTEGER PRIMARY KEY REFERENCES leads(id) ON DELETE CASCADE,
    time_spent_seconds FLOAT,
    buttons_clicked TEXT,
    cursor_hover_zones TEXT,
    return_count INTEGER DEFAULT 0,
    page_views INTEGER DEFAULT 0,
    scroll_depth_percent FLOAT,
    device_type VARCHAR(50),
    browser VARCHAR(100),
    os VARCHAR(100),
    screen_resolution VARCHAR(20),
    ip_address VARCHAR(45),
    user_agent TEXT,
    referrer VARCHAR(500),
    utm_source VARCHAR(255),
    utm_medium VARCHAR(255),
    utm_campaign VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Admin data table
CREATE TABLE IF NOT EXISTS admin_data (
    id SERIAL PRIMARY KEY,
    service_name TEXT,
    budget_range TEXT,
    available_products TEXT,
    contact_methods TEXT,
    form_settings JSONB,
    ui_config JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_leads_last_name ON leads(last_name);
CREATE INDEX IF NOT EXISTS idx_behaviors_lead_id ON behaviors(lead_id);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO crm_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO crm_user;
