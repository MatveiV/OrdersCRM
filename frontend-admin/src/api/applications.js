const API_BASE = '/api';

async function request(url, options = {}) {
    const token = localStorage.getItem('admin_access_token');
    const headers = { 'Content-Type': 'application/json', ...options.headers };
    if (token) headers.Authorization = `Bearer ${token}`;
    const response = await fetch(`${API_BASE}${url}`, { ...options, headers });
    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || `HTTP ${response.status}`);
    }
    return response.json();
}

export const applicationsApi = {
    getScored(skip = 0, limit = 100) {
        return request(`/applications/scored?skip=${skip}&limit=${limit}`);
    },
    getById(id) {
        return request(`/applications/${id}`);
    },
    getStats() {
        return request('/applications/stats');
    },
    update(id, data) {
        return request(`/applications/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },
    delete(id) {
        return request(`/applications/${id}`, { method: 'DELETE' });
    },
};
