import { applicationsApi } from '../api/applications.js';
import { ApplicationDetailModal } from '../components/ApplicationDetailModal.js';

function formatTime(seconds) {
    if (seconds < 60) return `${seconds} сек`;
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return s > 0 ? `${m} мин ${s} сек` : `${m} мин`;
}

export async function renderApplicationsPage(container) {
    container.innerHTML = `
        <header class="content-header">
            <h1 class="page-title">Заявки пользователей</h1>
            <button class="btn btn-secondary" id="apps-refresh-btn">Обновить</button>
        </header>
        <div class="apps-tabs">
            <button class="apps-tab active" data-tab="stats">Общая статистика</button>
            <button class="apps-tab" data-tab="list">Список заявок</button>
        </div>
        <div id="apps-content"></div>
    `;

    const content = document.getElementById('apps-content');
    let activeTab = 'stats';

    async function switchTab(tab) {
        activeTab = tab;
        document.querySelectorAll('.apps-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
        if (tab === 'stats') {
            await renderStats(content);
        } else {
            await renderList(content);
        }
    }

    document.querySelectorAll('.apps-tab').forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });
    document.getElementById('apps-refresh-btn').addEventListener('click', () => switchTab(activeTab));

    await switchTab('stats');
}

async function renderStats(container) {
    container.innerHTML = '<div class="stats-loader"><div class="spinner"></div><p>Загрузка статистики...</p></div>';
    try {
        const stats = await applicationsApi.getStats();

        const tempLabels = { hot: 'Горячих', warm: 'Тёплых', cold: 'Холодных' };
        const tempEmoji = { hot: '🔥', warm: '🌡', cold: '❄️' };
        const tempColors = { hot: 'var(--ddanger)', warm: '#F39C12', cold: '#3498DB' };

        container.innerHTML = `
            <div class="stats-section">
                <div class="stats-grid-4">
                    <div class="stats-card">
                        <span class="stats-card-value">${stats.total}</span>
                        <span class="stats-card-label">Всего заявок</span>
                    </div>
                    <div class="stats-card">
                        <span class="stats-card-value" style="color:${tempColors.hot}">${stats.hot_count}</span>
                        <span class="stats-card-label">${tempEmoji.hot} ${tempLabels.hot}</span>
                    </div>
                    <div class="stats-card">
                        <span class="stats-card-value" style="color:${tempColors.warm}">${stats.warm_count}</span>
                        <span class="stats-card-label">${tempEmoji.warm} ${tempLabels.warm}</span>
                    </div>
                    <div class="stats-card">
                        <span class="stats-card-value" style="color:${tempColors.cold}">${stats.cold_count}</span>
                        <span class="stats-card-label">${tempEmoji.cold} ${tempLabels.cold}</span>
                    </div>
                </div>
            </div>
            <div class="stats-section">
                <h3 class="stats-subtitle">Распределение по отделам</h3>
                <div class="histogram" id="apps-dept-histogram"></div>
            </div>
            <div class="stats-grid-3">
                <div class="stats-card">
                    <span class="stats-card-value">${stats.average_budget_max.toLocaleString('ru-RU')} ₽</span>
                    <span class="stats-card-label">Средний чек</span>
                </div>
                <div class="stats-card">
                    <span class="stats-card-value">${stats.average_deadline_weeks.toFixed(1)}</span>
                    <span class="stats-card-label">Средний срок (недель)</span>
                </div>
                <div class="stats-card">
                    <span class="stats-card-value">${stats.personal_manager_rate}%</span>
                    <span class="stats-card-label">Нужен перс. менеджер</span>
                </div>
            </div>
        `;

        // Render department histogram
        const histContainer = document.getElementById('apps-dept-histogram');
        if (stats.departments && stats.departments.length > 0) {
            const maxCount = Math.max(...stats.departments.map(d => d.count), 1);
            stats.departments.forEach(dept => {
                const row = document.createElement('div');
                row.className = 'histogram-row';
                const pct = (dept.count / maxCount) * 100;
                row.innerHTML = `
                    <span class="histogram-label">${dept.name}</span>
                    <div class="histogram-bar"><div class="histogram-bar-fill" style="width:${pct}%"></div></div>
                    <span class="histogram-value">${dept.count}</span>
                `;
                histContainer.appendChild(row);
            });
        }
    } catch (err) {
        container.innerHTML = `<div class="stats-error"><p>Ошибка: ${err.message}</p></div>`;
    }
}

async function renderList(container) {
    container.innerHTML = '<div class="stats-loader"><div class="spinner"></div><p>Загрузка заявок...</p></div>';
    try {
        const apps = await applicationsApi.getScored();
        const filterPills = document.createElement('div');
        filterPills.className = 'filter-pills';
        filterPills.innerHTML = `
            <button class="pill active" data-filter="all">Все</button>
            <button class="pill" data-filter="hot">Горячие</button>
            <button class="pill" data-filter="warm">Тёплые</button>
            <button class="pill" data-filter="cold">Холодные</button>
            <input type="text" class="search-input" placeholder="Поиск..." id="apps-search">
        `;

        const tableWrap = document.createElement('div');
        tableWrap.className = 'table-container';
        tableWrap.innerHTML = `
            <table class="data-table" id="apps-table">
                <thead>
                    <tr>
                        <th class="col-rank">#</th>
                        <th class="col-client">Клиент</th>
                        <th class="col-company">Компания</th>
                        <th class="col-budget">Бюджет</th>
                        <th class="col-deadline">Срок</th>
                        <th class="col-temp">Темп-ра</th>
                        <th class="col-actions">Действия</th>
                    </tr>
                </thead>
                <tbody id="apps-tbody"></tbody>
            </table>
        `;

        container.innerHTML = '';
        container.appendChild(filterPills);
        container.appendChild(tableWrap);

        const tbody = document.getElementById('apps-tbody');
        let currentFilter = 'all';
        let searchQuery = '';

        function getTempBadge(scoring) {
            if (!scoring) return '<span class="badge badge-inactive">—</span>';
            const config = {
                hot: { cls: 'badge-hot', label: 'Горячий', emoji: '🔥' },
                warm: { cls: 'badge-warm', label: 'Тёплый', emoji: '🌡' },
                cold: { cls: 'badge-cold', label: 'Холодный', emoji: '❄️' },
            };
            const c = config[scoring.temperature] || config.cold;
            return `<span class="badge ${c.cls}">${c.emoji} ${c.label} (${scoring.score})</span>`;
        }

        function filterApps(list) {
            return list.filter(app => {
                if (currentFilter !== 'all' && app.scoring && app.scoring.temperature !== currentFilter) return false;
                if (searchQuery) {
                    const q = searchQuery.toLowerCase();
                    const fullName = `${app.first_name} ${app.last_name}`.toLowerCase();
                    const niche = (app.business_niche || '').toLowerCase();
                    if (!fullName.includes(q) && !niche.includes(q)) return false;
                }
                return true;
            });
        }

        function renderTable(list) {
            const filtered = filterApps(list);
            if (filtered.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:40px;color:var(--dtext-secondary)">Нет заявок по выбранному фильтру</td></tr>';
                return;
            }
            tbody.innerHTML = '';
            filtered.forEach((app, idx) => {
                const sc = app.scoring || {};
                const budgetDisplay = app.budget ? (() => {
                    try {
                        const b = JSON.parse(app.budget);
                        const v = b.max || b.min || 0;
                        return `${parseInt(v).toLocaleString('ru-RU')} ₽`;
                    } catch { return app.budget; }
                })() : '—';
                const niche = app.business_niche || '';
                const size = app.company_size || '';
                const companyShort = size ? `${niche}, ${size}` : niche || '—';

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="col-rank">${idx + 1}</td>
                    <td class="col-client">
                        <strong>${app.first_name} ${app.last_name}</strong>
                        <div class="sub-text">${app.contact_data || ''}</div>
                    </td>
                    <td class="col-company">${companyShort}</td>
                    <td class="col-budget">${budgetDisplay}</td>
                    <td class="col-deadline">${app.project_deadline || '—'}</td>
                    <td class="col-temp">${getTempBadge(sc)}</td>
                    <td class="col-actions">
                        <button class="action-btn view-btn" title="Просмотр" data-id="${app.id}">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });

            tbody.querySelectorAll('.view-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const id = parseInt(btn.dataset.id);
                    const app = apps.find(a => a.id === id);
                    if (app) new ApplicationDetailModal(app, () => renderTable(apps));
                });
            });
        }

        document.querySelectorAll('.filter-pills .pill').forEach(pill => {
            pill.addEventListener('click', () => {
                document.querySelectorAll('.filter-pills .pill').forEach(p => p.classList.remove('active'));
                pill.classList.add('active');
                currentFilter = pill.dataset.filter;
                renderTable(apps);
            });
        });

        document.getElementById('apps-search').addEventListener('input', (e) => {
            searchQuery = e.target.value;
            renderTable(apps);
        });

        renderTable(apps);

    } catch (err) {
        container.innerHTML = `<div class="stats-error"><p>Ошибка: ${err.message}</p></div>`;
    }
}
