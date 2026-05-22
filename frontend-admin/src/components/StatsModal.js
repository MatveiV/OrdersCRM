import { getBehaviorStats } from '../api/stats.js';

function formatTime(seconds) {
    if (seconds < 60) return `${seconds} сек`;
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return s > 0 ? `${m} мин ${s} сек` : `${m} мин`;
}

function getHeatColor(frequency, maxFreq) {
    const ratio = maxFreq > 0 ? frequency / maxFreq : 0;
    const r = Math.min(255, Math.round(ratio * 255));
    const g = Math.min(255, Math.round((1 - Math.abs(ratio - 0.5) * 2) * 200));
    const b = Math.min(255, Math.round((1 - ratio) * 255));
    return `rgba(${r}, ${g}, ${b}, 0.5)`;
}

function renderHeatmap(data) {
    const container = document.createElement('div');
    container.className = 'heatmap-container';
    container.style.cssText = 'position:relative;width:100%;height:400px;background:#f5f5f5;border-radius:8px;overflow:hidden;';

    const canvas = document.createElement('canvas');
    canvas.width = container.clientWidth || 900;
    canvas.height = 400;
    canvas.style.cssText = 'width:100%;height:100%;';
    container.appendChild(canvas);

    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;

    ctx.fillStyle = '#f8f9fa';
    ctx.fillRect(0, 0, w, h);

    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 1;
    for (let x = 0; x <= w; x += 100) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();
    }
    for (let y = 0; y <= h; y += 100) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
    }

    const maxFreq = Math.max(...data.map(d => d.frequency), 1);

    data.forEach(point => {
        const radius = Math.max(5, Math.min(40, (point.frequency / maxFreq) * 40));
        const color = getHeatColor(point.frequency, maxFreq);
        ctx.beginPath();
        ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
    });

    return container;
}

export async function renderStatsView(container) {
    container.innerHTML = `
        <header class="content-header">
            <h1 class="page-title">Статистика пользователей</h1>
        </header>
        <div class="stats-page" id="stats-page">
            <div class="stats-loader">
                <div class="spinner"></div>
                <p>Загрузка статистики...</p>
            </div>
        </div>
    `;

    const statsContainer = document.getElementById('stats-page');

    try {
        const stats = await getBehaviorStats();
        statsContainer.innerHTML = '';

        // Section 1: Time stats
        const timeSection = document.createElement('div');
        timeSection.className = 'stats-section';
        timeSection.innerHTML = `
            <h3 class="stats-subtitle">⏱ Время на странице (среднее / максимальное)</h3>
            <table class="stats-table">
                <thead>
                    <tr><th>Период</th><th>Среднее время</th><th>Максимальное время</th></tr>
                </thead>
                <tbody>
                    <tr><td>За сегодня</td><td>${formatTime(stats.avg_time_on_page.daily)}</td><td>${formatTime(stats.max_time_on_page.daily)}</td></tr>
                    <tr><td>За неделю</td><td>${formatTime(stats.avg_time_on_page.weekly)}</td><td>${formatTime(stats.max_time_on_page.weekly)}</td></tr>
                    <tr><td>За месяц</td><td>${formatTime(stats.avg_time_on_page.monthly)}</td><td>${formatTime(stats.max_time_on_page.monthly)}</td></tr>
                </tbody>
            </table>
        `;
        statsContainer.appendChild(timeSection);

        // Section 2: Top buttons
        if (stats.top_buttons && stats.top_buttons.length > 0) {
            const btnSection = document.createElement('div');
            btnSection.className = 'stats-section';
            btnSection.innerHTML = '<h3 class="stats-subtitle">🔘 Самые нажимаемые элементы</h3>';
            const barContainer = document.createElement('div');
            barContainer.className = 'histogram';
            const maxClicks = Math.max(...stats.top_buttons.map(b => b.clicks), 1);
            stats.top_buttons.forEach(item => {
                const row = document.createElement('div');
                row.className = 'histogram-row';
                const pct = (item.clicks / maxClicks) * 100;
                const fill = document.createElement('div');
                fill.className = 'histogram-bar-fill';
                fill.style.width = `${Math.min(pct, 100)}%`;
                row.innerHTML = `
                    <span class="histogram-label">${item.button}</span>
                    <div class="histogram-bar"></div>
                    <span class="histogram-value">${item.clicks}</span>
                `;
                row.querySelector('.histogram-bar').appendChild(fill);
                barContainer.appendChild(row);
            });
            btnSection.appendChild(barContainer);
            statsContainer.appendChild(btnSection);
        }

        // Section 3: Heatmap
        if (stats.heatmap_data && stats.heatmap_data.length > 0) {
            const heatSection = document.createElement('div');
            heatSection.className = 'stats-section';
            heatSection.innerHTML = '<h3 class="stats-subtitle">🖱 Тепловая карта курсора (heatmap)</h3>';
            heatSection.appendChild(renderHeatmap(stats.heatmap_data));
            statsContainer.appendChild(heatSection);
        }

        // Section 4: General info
        const genSection = document.createElement('div');
        genSection.className = 'stats-section';
        genSection.innerHTML = `
            <h3 class="stats-subtitle">📈 Общие показатели</h3>
            <div class="stats-grid">
                <div class="stats-card">
                    <span class="stats-card-value">${stats.total_sessions}</span>
                    <span class="stats-card-label">Всего сессий</span>
                </div>
                <div class="stats-card">
                    <span class="stats-card-value">${stats.total_metrics_records}</span>
                    <span class="stats-card-label">Всего записей метрик</span>
                </div>
            </div>
        `;
        statsContainer.appendChild(genSection);

    } catch (err) {
        statsContainer.innerHTML = `
            <div class="stats-error">
                <p>Ошибка загрузки статистики: ${err.message}</p>
                <button class="btn btn-primary" id="stats-retry-btn">Повторить</button>
            </div>
        `;
        document.getElementById('stats-retry-btn').addEventListener('click', () => {
            renderStatsView(container);
        });
    }
}
