const TOKEN_KEY = 'admin_access_token';
const REFRESH_KEY = 'admin_refresh_token';
const API_BASE = '/api';

async function refreshToken() {
    const refresh = localStorage.getItem(REFRESH_KEY);
    if (!refresh) return false;
    try {
        const res = await fetch(`${API_BASE}/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refresh }),
        });
        if (!res.ok) return false;
        const data = await res.json();
        localStorage.setItem(TOKEN_KEY, data.access_token);
        localStorage.setItem(REFRESH_KEY, data.refresh_token);
        return true;
    } catch {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(REFRESH_KEY);
        return false;
    }
}

async function apiClient(url, options = {}) {
    const makeRequest = async (token) => {
        const headers = { ...options.headers };
        if (token) {
            headers.Authorization = `Bearer ${token}`;
        }
        return fetch(`${API_BASE}${url}`, { ...options, headers });
    };

    let token = localStorage.getItem(TOKEN_KEY);
    let response = await makeRequest(token);

    if (response.status === 401 && token) {
        const refreshed = await refreshToken();
        if (refreshed) {
            token = localStorage.getItem(TOKEN_KEY);
            response = await makeRequest(token);
        } else {
            window.location.hash = '/login';
            throw new Error('Session expired');
        }
    }

    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || `HTTP ${response.status}`);
    }

    return response.json();
}

export { apiClient };
