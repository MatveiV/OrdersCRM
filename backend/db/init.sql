-- Orders CRM Database Initialization

-- Create leads table for warm clients
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Contact information
    contact_name VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(50),
    contact_email VARCHAR(255),

    -- Business information
    business_info TEXT,
    budget VARCHAR(100),
    contact_method VARCHAR(50),
    comments TEXT,

    -- Lead metrics (aggregated by frontend)
    lead_metrics JSONB,
    technical_info JSONB,

    -- UTM parameters
    source_url TEXT,
    utm_source VARCHAR(255),
    utm_medium VARCHAR(255),
    utm_campaign VARCHAR(255),

    -- Technical info
    ip_address INET,
    user_agent TEXT,

    -- Status
    status VARCHAR(50) DEFAULT 'new',
    processed BOOLEAN DEFAULT FALSE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_contact_email ON leads(contact_email);
CREATE INDEX IF NOT EXISTS idx_leads_contact_phone ON leads(contact_phone);

-- Lead source tracking table
CREATE TABLE IF NOT EXISTS lead_sources (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default sources
INSERT INTO lead_sources (source_name) VALUES
    ('website'),
    ('landing_page'),
    ('form_direct'),
    ('referral')
ON CONFLICT DO NOTHING;

-- Create audit log for data changes
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    table_name VARCHAR(100),
    record_id INTEGER,
    action VARCHAR(50),
    old_data JSONB,
    new_data JSONB,
    changed_by VARCHAR(255)
);

-- Function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for leads
CREATE TRIGGER update_leads_timestamp
    BEFORE UPDATE ON leads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO crm_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO crm_user;