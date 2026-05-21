const API_BASE = '';

export async function getAdminData() {
    try {
        const response = await fetch(`${API_BASE}/api/admin/active`);
        if (!response.ok) throw new Error('Failed to fetch admin data');
        return await response.json();
    } catch (error) {
        console.warn('Admin data not available, using defaults:', error);
        return getDefaultAdminData();
    }
}

export async function submitLead(data) {
    try {
        const response = await fetch(`${API_BASE}/api/leads/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Failed to submit lead');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Submit error:', error);
        throw error;
    }
}

function getDefaultAdminData() {
    return {
        service_name: 'CRM системы, ERP решения, Автоматизация бизнеса',
        budget_range: JSON.stringify({ min: 100000, max: 5000000 }),
        available_products: 'CRM, ERP, LMS, TMS, POS, Складской учет',
        contact_methods: 'email, phone, telegram, whatsapp',
        form_settings: { required_fields: ['first_name', 'last_name', 'contact_data'] },
        ui_config: { theme: 'dark' }
    };
}
