const API_BASE = '/api';

async function request(url, options = {}) {
    const response = await fetch(`${API_BASE}${url}`, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options,
    });
    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || `HTTP ${response.status}`);
    }
    return response.json();
}

export const authApi = {
    async login(username, password) {
        return request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
    },

    async register(username, password) {
        return request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
    },

    async refresh(refreshToken) {
        return request('/auth/refresh', {
            method: 'POST',
            body: JSON.stringify({ refresh_token: refreshToken }),
        });
    },

    async check() {
        return request('/auth/check');
    },

    async getMe(accessToken) {
        return request('/auth/me', {
            headers: { Authorization: `Bearer ${accessToken}` },
        });
    },
};
