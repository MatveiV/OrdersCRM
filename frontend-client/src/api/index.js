const API_BASE = '/api';

export async function getAdminData() {
    try {
        const response = await fetch(`${API_BASE}/admin/active`);
        if (!response.ok) throw new Error('Failed to fetch admin data');
        return await response.json();
    } catch (error) {
        console.warn('Admin data unavailable, using defaults:', error);
        return {};
    }
}

export async function submitLead(payload) {
    const response = await fetch(`${API_BASE}/leads/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || 'Failed to submit lead');
    }
    
    return await response.json();
}
