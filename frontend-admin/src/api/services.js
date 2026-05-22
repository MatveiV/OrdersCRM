const API_BASE = '/api';

async function request(url, options = {}) {
    const token = localStorage.getItem('admin_access_token');
    const headers = { 'Content-Type': 'application/json', ...options.headers };
    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }
    const response = await fetch(`${API_BASE}${url}`, { ...options, headers });
    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || `HTTP ${response.status}`);
    }
    return response.json();
}

export const servicesApi = {
    getAll() {
        return request('/admin/services');
    },

    getById(id) {
        return request(`/admin/services/${id}`);
    },

    create(data) {
        return request('/admin/services', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    update(id, data) {
        return request(`/admin/services/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    delete(id) {
        return request(`/admin/services/${id}`, {
            method: 'DELETE',
        });
    },
};
