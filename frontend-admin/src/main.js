import './styles/main.css';
import { authApi } from './api/auth.js';
import { servicesApi } from './api/services.js';

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

// ---- Toast System ----

let toastId = 0;

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const id = ++toastId;
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.id = `toast-${id}`;
    toast.innerHTML = `
        <span class="toast-icon">${type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ'}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="document.getElementById('toast-${id}').remove()">&times;</button>
    `;
    container.appendChild(toast);
    setTimeout(() => {
        const el = document.getElementById(`toast-${id}`);
        if (el) {
            el.style.opacity = '0';
            el.style.transform = 'translateX(100%)';
            setTimeout(() => el.remove(), 300);
        }
    }, 4000);
}

// ---- Confirm Dialog ----

function showConfirm(message) {
    return new Promise((resolve) => {
        const overlay = document.createElement('div');
        overlay.className = 'confirm-overlay';
        overlay.innerHTML = `
            <div class="confirm-dialog">
                <p class="confirm-message">${message}</p>
                <div class="confirm-actions">
                    <button class="btn btn-secondary" id="confirm-cancel">Отмена</button>
                    <button class="btn btn-danger" id="confirm-ok">Удалить</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.remove();
                resolve(false);
            }
        });
        document.getElementById('confirm-cancel').addEventListener('click', () => {
            overlay.remove();
            resolve(false);
        });
        document.getElementById('confirm-ok').addEventListener('click', () => {
            overlay.remove();
            resolve(true);
        });
    });
}

// ---- Service Modal ----

function openServiceModal(service = null) {
    const isEdit = !!service;
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';

    let budgetMin = '', budgetMax = '', budgetStep = '';
    if (isEdit && service.budget_range) {
        try {
            const range = JSON.parse(service.budget_range);
            budgetMin = range.min || '';
            budgetMax = range.max || '';
            budgetStep = range.step || '';
        } catch {}
    }

    overlay.innerHTML = `
        <div class="modal-container">
            <div class="modal-header">
                <h2>${isEdit ? 'Редактировать услугу' : 'Добавить услугу'}</h2>
                <button class="modal-close" id="modal-close">&times;</button>
            </div>
            <form id="service-form" class="modal-form">
                <div class="form-group">
                    <label for="srv-name">Название услуги <span class="required">*</span></label>
                    <input type="text" id="srv-name" required maxlength="200" placeholder="Введите название" value="${isEdit ? service.service_name : ''}">
                    <span class="form-error" id="name-error"></span>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="srv-task-type">Тип задачи</label>
                        <input type="text" id="srv-task-type" placeholder="Например: Разработка" value="${isEdit && service.task_type ? service.task_type : ''}">
                    </div>
                    <div class="form-group">
                        <label for="srv-product">Интересующий продукт</label>
                        <input type="text" id="srv-product" placeholder="Например: CRM" value="${isEdit && service.product_interest ? service.product_interest : ''}">
                    </div>
                </div>
                <div class="form-row form-row-3">
                    <div class="form-group">
                        <label for="srv-budget-min">Бюджет (от)</label>
                        <input type="number" id="srv-budget-min" placeholder="0" min="0" value="${budgetMin}">
                    </div>
                    <div class="form-group">
                        <label for="srv-budget-max">Бюджет (до)</label>
                        <input type="number" id="srv-budget-max" placeholder="0" min="0" value="${budgetMax}">
                    </div>
                    <div class="form-group">
                        <label for="srv-budget-step">Шаг</label>
                        <input type="number" id="srv-budget-step" placeholder="10000" min="1" value="${budgetStep}">
                    </div>
                </div>
                <div class="form-group">
                    <label for="srv-desc">Описание</label>
                    <textarea id="srv-desc" rows="3" placeholder="Описание услуги">${isEdit && service.description ? service.description : ''}</textarea>
                </div>
                <div class="form-group form-checkbox">
                    <label class="checkbox-label">
                        <input type="checkbox" id="srv-active" ${isEdit ? (service.is_active ? 'checked' : '') : 'checked'}>
                        <span>Услуга активна</span>
                    </label>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" id="modal-cancel">Отмена</button>
                    <button type="submit" class="btn btn-primary">${isEdit ? 'Сохранить изменения' : 'Создать услугу'}</button>
                </div>
            </form>
        </div>
    `;

    document.body.appendChild(overlay);

    function close() { overlay.remove(); }

    document.getElementById('modal-close').addEventListener('click', close);
    document.getElementById('modal-cancel').addEventListener('click', close);
    overlay.addEventListener('click', (e) => { if (e.target === overlay) close(); });

    document.getElementById('service-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('srv-name').value.trim();
        const nameError = document.getElementById('name-error');

        if (!name) {
            nameError.textContent = 'Название услуги обязательно';
            return;
        }
        nameError.textContent = '';

        const min = parseInt(document.getElementById('srv-budget-min').value) || 0;
        const max = parseInt(document.getElementById('srv-budget-max').value) || 0;
        const step = parseInt(document.getElementById('srv-budget-step').value) || 0;

        if (max && min && max <= min) {
            nameError.textContent = 'Максимальная сумма должна быть больше минимальной';
            return;
        }

        const budgetRange = (min || max || step)
            ? JSON.stringify({ min, max, step })
            : null;

        const payload = {
            service_name: name,
            task_type: document.getElementById('srv-task-type').value.trim() || null,
            product_interest: document.getElementById('srv-product').value.trim() || null,
            budget_range: budgetRange,
            description: document.getElementById('srv-desc').value.trim() || null,
            is_active: document.getElementById('srv-active').checked,
        };

        try {
            if (isEdit) {
                await servicesApi.update(service.id, payload);
                showToast('Изменения сохранены', 'success');
            } else {
                await servicesApi.create(payload);
                showToast('Услуга успешно добавлена', 'success');
            }
            close();
            await loadServices();
        } catch (err) {
            showToast(err.message || 'Ошибка при сохранении', 'error');
        }
    });
}

// ---- Load & Render Services ----

let currentAdmin = null;

async function loadServices() {
    const tableBody = document.getElementById('services-tbody');
    const emptyState = document.getElementById('empty-state');
    const errorState = document.getElementById('error-state');

    tableBody.innerHTML = '';
    emptyState.style.display = 'none';
    errorState.style.display = 'none';

    try {
        const services = await servicesApi.getAll();

        if (!Array.isArray(services)) {
            errorState.style.display = 'block';
            errorState.querySelector('.error-text').textContent = 'Некорректный формат данных от сервера';
            return;
        }

        if (services.length === 0) {
            emptyState.style.display = 'block';
            return;
        }

        services.forEach(s => {
            let budgetDisplay = '—';
            if (s.budget_range) {
                try {
                    const r = JSON.parse(s.budget_range);
                    const fmt = (v) => parseInt(v).toLocaleString('ru-RU');
                    if (r.min && r.max) budgetDisplay = `${fmt(r.min)} – ${fmt(r.max)} ₽`;
                    else if (r.min) budgetDisplay = `от ${fmt(r.min)} ₽`;
                    else if (r.max) budgetDisplay = `до ${fmt(r.max)} ₽`;
                } catch {
                    budgetDisplay = s.budget_range;
                }
            }

            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="col-id">${s.id}</td>
                <td class="col-name">${s.service_name}</td>
                <td class="col-type">${s.task_type || '—'}</td>
                <td class="col-budget">${budgetDisplay}</td>
                <td class="col-product">${s.product_interest || '—'}</td>
                <td class="col-status">
                    <span class="badge ${s.is_active ? 'badge-active' : 'badge-inactive'}">
                        ${s.is_active ? 'Активна' : 'Неактивна'}
                    </span>
                </td>
                <td class="col-actions">
                    <button class="action-btn edit-btn" title="Редактировать" data-id="${s.id}">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                    </button>
                    <button class="action-btn delete-btn" title="Удалить" data-id="${s.id}" data-name="${s.service_name}">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });

        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = parseInt(btn.dataset.id);
                const service = services.find(s => s.id === id);
                if (service) openServiceModal(service);
            });
        });

        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = parseInt(btn.dataset.id);
                const name = btn.dataset.name;
                const ok = await showConfirm(`Вы уверены, что хотите удалить услугу "${name}"? Это действие нельзя отменить.`);
                if (!ok) return;
                try {
                    await servicesApi.delete(id);
                    showToast('Услуга удалена', 'success');
                    await loadServices();
                } catch (err) {
                    showToast(err.message || 'Ошибка при удалении', 'error');
                }
            });
        });
    } catch (err) {
        errorState.style.display = 'block';
        errorState.querySelector('.error-text').textContent = err.message || 'Не удалось загрузить список услуг';
    }
}

// ---- Dashboard Render ----

function renderDashboard(admin) {
    currentAdmin = admin;
    const app = document.getElementById('app');
    app.innerHTML = `
        <div class="dashboard">
            <aside class="sidebar">
                <div class="sidebar-header">
                    <h2 class="sidebar-title">Orders CRM</h2>
                </div>
                <nav class="sidebar-nav">
                    <a class="nav-item active" href="#/dashboard">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
                        <span>Услуги</span>
                    </a>
                    <a class="nav-item disabled" href="#">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
                        <span>Заявки</span>
                    </a>
                </nav>
                <div class="sidebar-footer">
                    <span class="sidebar-user">${admin.username}</span>
                    <button id="logout-btn" class="logout-link">Выйти</button>
                </div>
            </aside>
            <main class="main-content">
                <header class="content-header">
                    <h1 class="page-title">Управление услугами</h1>
                    <button id="add-service-btn" class="btn btn-primary">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                        Добавить услугу
                    </button>
                </header>

                <div id="toast-container" class="toast-container"></div>

                <div class="table-container">
                    <div id="error-state" class="empty-state" style="display:none;">
                        <p class="error-text"></p>
                        <button class="btn btn-secondary" id="retry-btn">Повторить</button>
                    </div>
                    <div id="empty-state" class="empty-state" style="display:none;">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="empty-icon"><path d="M13 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V9z"/><polyline points="13 2 13 9 20 9"/></svg>
                        <p>Нет услуг. Нажмите «Добавить услугу», чтобы создать первую.</p>
                    </div>
                    <table class="services-table" id="services-table">
                        <thead>
                            <tr>
                                <th class="col-id">ID</th>
                                <th class="col-name">Название услуги</th>
                                <th class="col-type">Тип задачи</th>
                                <th class="col-budget">Диапазон бюджета</th>
                                <th class="col-product">Продукт</th>
                                <th class="col-status">Статус</th>
                                <th class="col-actions">Действия</th>
                            </tr>
                        </thead>
                        <tbody id="services-tbody"></tbody>
                    </table>
                </div>
            </main>
        </div>
    `;

    document.getElementById('logout-btn').addEventListener('click', () => {
        clearTokens();
        navigate('/login');
        render();
    });

    document.getElementById('add-service-btn').addEventListener('click', () => {
        openServiceModal(null);
    });

    const retryBtn = document.getElementById('retry-btn');
    if (retryBtn) {
        retryBtn.addEventListener('click', loadServices);
    }

    loadServices();
}

// ---- Login Pages (unchanged from before) ----

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

window.addEventListener('hashchange', render);
document.addEventListener('DOMContentLoaded', render);
