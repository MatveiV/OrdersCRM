import './styles/main.css';
import { authApi } from './api/auth.js';

const TOKEN_KEY = 'admin_access_token';
const REFRESH_KEY = 'admin_refresh_token';

function getTokens() {
    return {
        access: localStorage.getItem(TOKEN_KEY),
        refresh: localStorage.getItem(REFRESH_KEY),
    };
}

function saveTokens(access, refresh) {
    localStorage.setItem(TOKEN_KEY, access);
    localStorage.setItem(REFRESH_KEY, refresh);
}

function clearTokens() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
}

async function tryRefreshToken() {
    const { refresh } = getTokens();
    if (!refresh) return false;
    try {
        const result = await authApi.refresh(refresh);
        saveTokens(result.access_token, result.refresh_token);
        return true;
    } catch {
        clearTokens();
        return false;
    }
}

async function checkAuth() {
    const { access } = getTokens();
    if (!access) return null;
    try {
        return await authApi.getMe(access);
    } catch {
        const refreshed = await tryRefreshToken();
        if (refreshed) {
            const { access: newAccess } = getTokens();
            return await authApi.getMe(newAccess);
        }
        return null;
    }
}

function navigate(hash) {
    window.location.hash = hash;
}

function getRoute() {
    return window.location.hash.slice(1) || '/login';
}

async function render() {
    const admin = await checkAuth();
    const route = getRoute();

    if (admin) {
        if (route === '/dashboard') {
            renderDashboard(admin);
        } else {
            navigate('/dashboard');
        }
    } else {
        if (route === '/login') {
            renderLogin();
        } else {
            navigate('/login');
        }
    }
}

function renderLogin() {
    const app = document.getElementById('app');

    authApi.check().then(({ has_admins }) => {
        if (has_admins) {
            app.innerHTML = `
                <div class="auth-container">
                    <div class="auth-card">
                        <h1 class="auth-title">Orders CRM</h1>
                        <p class="auth-subtitle">Вход в админ-панель</p>
                        <form id="login-form" class="auth-form">
                            <div class="form-group">
                                <label for="username">Логин</label>
                                <input type="text" id="username" name="username" required placeholder="Введите логин" autocomplete="username">
                                <span class="error-msg"></span>
                            </div>
                            <div class="form-group">
                                <label for="password">Пароль</label>
                                <input type="password" id="password" name="password" required placeholder="Введите пароль" autocomplete="current-password">
                                <span class="error-msg"></span>
                            </div>
                            <div id="auth-error" class="auth-error" style="display:none;"></div>
                            <button type="submit" class="auth-btn">Войти</button>
                        </form>
                        <div class="auth-loader" style="display:none;">
                            <div class="spinner"></div>
                            <p>Вход...</p>
                        </div>
                    </div>
                </div>
            `;
            setupLoginForm();
        } else {
            app.innerHTML = `
                <div class="auth-container">
                    <div class="auth-card">
                        <h1 class="auth-title">Orders CRM</h1>
                        <p class="auth-subtitle">Регистрация администратора</p>
                        <form id="register-form" class="auth-form">
                            <div class="form-group">
                                <label for="username">Логин</label>
                                <input type="text" id="username" name="username" required placeholder="Придумайте логин" autocomplete="username">
                                <span class="error-msg"></span>
                            </div>
                            <div class="form-group">
                                <label for="password">Пароль</label>
                                <input type="password" id="password" name="password" required placeholder="Минимум 6 символов" autocomplete="new-password">
                                <span class="error-msg"></span>
                            </div>
                            <div class="form-group">
                                <label for="confirm-password">Подтверждение пароля</label>
                                <input type="password" id="confirm-password" name="confirm_password" required placeholder="Повторите пароль" autocomplete="new-password">
                                <span class="error-msg"></span>
                            </div>
                            <div id="auth-error" class="auth-error" style="display:none;"></div>
                            <button type="submit" class="auth-btn">Зарегистрироваться</button>
                        </form>
                        <div class="auth-loader" style="display:none;">
                            <div class="spinner"></div>
                            <p>Регистрация...</p>
                        </div>
                    </div>
                </div>
            `;
            setupRegisterForm();
        }
    });
}

function setupLoginForm() {
    const form = document.getElementById('login-form');
    const errorDiv = document.getElementById('auth-error');
    const loader = document.querySelector('.auth-loader');
    const btn = form.querySelector('.auth-btn');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorDiv.style.display = 'none';
        btn.style.display = 'none';
        loader.style.display = 'block';

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        try {
            const result = await authApi.login(username, password);
            saveTokens(result.access_token, result.refresh_token);
            navigate('/dashboard');
            render();
        } catch (err) {
            errorDiv.textContent = err.message || 'Неверный логин или пароль';
            errorDiv.style.display = 'block';
            btn.style.display = 'block';
            loader.style.display = 'none';
        }
    });
}

function setupRegisterForm() {
    const form = document.getElementById('register-form');
    const errorDiv = document.getElementById('auth-error');
    const loader = document.querySelector('.auth-loader');
    const btn = form.querySelector('.auth-btn');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorDiv.style.display = 'none';

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        const confirm = document.getElementById('confirm-password').value;

        if (username.length < 3) {
            errorDiv.textContent = 'Логин должен быть минимум 3 символа';
            errorDiv.style.display = 'block';
            return;
        }
        if (password.length < 6) {
            errorDiv.textContent = 'Пароль должен быть минимум 6 символов';
            errorDiv.style.display = 'block';
            return;
        }
        if (password !== confirm) {
            errorDiv.textContent = 'Пароли не совпадают';
            errorDiv.style.display = 'block';
            return;
        }

        btn.style.display = 'none';
        loader.style.display = 'block';

        try {
            const result = await authApi.register(username, password);
            saveTokens(result.access_token, result.refresh_token);
            navigate('/dashboard');
            render();
        } catch (err) {
            errorDiv.textContent = err.message || 'Ошибка регистрации';
            errorDiv.style.display = 'block';
            btn.style.display = 'block';
            loader.style.display = 'none';
        }
    });
}

function renderDashboard(admin) {
    const app = document.getElementById('app');
    app.innerHTML = `
        <div class="dashboard-container">
            <header class="dashboard-header">
                <h1 class="dashboard-title">Orders CRM</h1>
                <button id="logout-btn" class="logout-btn">Выйти</button>
            </header>
            <main class="dashboard-main">
                <div class="welcome-card">
                    <h2>Добро пожаловать, ${admin.username}!</h2>
                    <p class="welcome-meta">Администратор с ${new Date(admin.created_at).toLocaleDateString('ru-RU')}</p>
                </div>
                <div class="dashboard-placeholder">
                    <div class="placeholder-icon">
                        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                            <path d="M9 14l2 2 4-4"/>
                        </svg>
                    </div>
                    <h3>Функционал панели управления</h3>
                    <p>Здесь будут отображаться лиды, аналитика поведения и настройки</p>
                </div>
            </main>
        </div>
    `;

    document.getElementById('logout-btn').addEventListener('click', () => {
        clearTokens();
        navigate('/login');
        render();
    });
}

window.addEventListener('hashchange', render);
document.addEventListener('DOMContentLoaded', render);
