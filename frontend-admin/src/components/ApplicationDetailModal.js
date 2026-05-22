import { applicationsApi } from '../api/applications.js';

export class ApplicationDetailModal {
    constructor(app, onUpdate) {
        this.app = app;
        this.onUpdate = onUpdate;
        this.overlay = document.createElement('div');
        this.overlay.className = 'modal-overlay';
        this.render();
        document.body.appendChild(this.overlay);
        this.bindEvents();
    }

    getTempBadge(sc) {
        if (!sc) return { cls: 'badge-inactive', label: '—', emoji: '' };
        const config = {
            hot: { cls: 'badge-hot', label: 'Горячий', emoji: '🔥', color: '#E74C3C' },
            warm: { cls: 'badge-warm', label: 'Тёплый', emoji: '🌡', color: '#F39C12' },
            cold: { cls: 'badge-cold', label: 'Холодный', emoji: '❄️', color: '#3498DB' },
        };
        return config[sc.temperature] || config.cold;
    }

    statuses = ['Новая', 'Связались', 'В работе', 'Договор', 'Оплачено', 'Архив'];

    async changeStatus(newStatus) {
        try {
            const updated = await applicationsApi.update(this.app.id, { status: newStatus });
            this.app.status = updated.status;
            this.app.notes = updated.notes;
            this.updateStatusUI();
            if (this.onUpdate) this.onUpdate(updated);
        } catch (e) {
            alert('Ошибка при изменении статуса: ' + e.message);
        }
    }

    async contact() {
        const now = new Date().toLocaleString('ru-RU');
        const note = `[${now}] Связались с клиентом`;
        const currentNotes = this.app.notes || '';
        const newNotes = currentNotes ? currentNotes + '\n' + note : note;
        try {
            const updated = await applicationsApi.update(this.app.id, {
                status: 'Связались',
                notes: newNotes,
            });
            this.app.status = updated.status;
            this.app.notes = updated.notes;
            this.updateStatusUI();
            this.renderNotes();
            if (this.onUpdate) this.onUpdate(updated);
        } catch (e) {
            alert('Ошибка: ' + e.message);
        }
    }

    async addNote() {
        const textarea = this.overlay.querySelector('#note-text');
        const text = textarea.value.trim();
        if (!text) return;
        const now = new Date().toLocaleString('ru-RU');
        const note = `[${now}] ${text}`;
        const currentNotes = this.app.notes || '';
        const newNotes = currentNotes ? currentNotes + '\n' + note : note;
        try {
            const updated = await applicationsApi.update(this.app.id, { notes: newNotes });
            this.app.notes = updated.notes;
            textarea.value = '';
            this.renderNotes();
            if (this.onUpdate) this.onUpdate(updated);
        } catch (e) {
            alert('Ошибка при добавлении заметки: ' + e.message);
        }
    }

    updateStatusUI() {
        const el = this.overlay.querySelector('#app-status-display');
        const dropdown = this.overlay.querySelector('#status-select');
        if (el) el.textContent = this.app.status;
        if (dropdown) dropdown.value = this.app.status;
    }

    renderNotes() {
        const container = this.overlay.querySelector('#notes-container');
        if (!container) return;
        const notes = (this.app.notes || '').split('\n').filter(Boolean);
        container.innerHTML = notes.length > 0
            ? notes.map(n => `<div class="note-item">${n}</div>`).join('')
            : '<div class="note-empty">Нет заметок</div>';
    }

    render() {
        const app = this.app;
        const sc = app.scoring || {};
        const breakdown = sc.score_breakdown || {};
        const tempBadge = this.getTempBadge(sc);
        const maxScore = 100;

        const breakdownBars = [
            { label: 'Бюджет', key: 'budget_score', max: 25 },
            { label: 'Компания', key: 'company_size_score', max: 20 },
            { label: 'Срок', key: 'deadline_score', max: 15 },
            { label: 'Роль', key: 'role_score', max: 10 },
            { label: 'Объём', key: 'task_volume_score', max: 10 },
            { label: 'Ниша', key: 'business_niche_score', max: 10 },
            { label: 'Контакты', key: 'contact_completeness_score', max: 5 },
            { label: 'Комментарий', key: 'comment_score', max: 5 },
        ];

        const fmtBudget = app.budget ? (() => {
            try {
                const b = JSON.parse(app.budget);
                const parts = [];
                if (b.min) parts.push(`${parseInt(b.min).toLocaleString('ru-RU')} ₽`);
                if (b.max) parts.push(`${parseInt(b.max).toLocaleString('ru-RU')} ₽`);
                return parts.join(' – ') || app.budget;
            } catch { return app.budget; }
        })() : '—';

        const insights = sc.insights || [];

        this.overlay.innerHTML = `
            <div class="modal-container modal-wide">
                <div class="modal-header">
                    <h2>Заявка #${app.id} — ${app.first_name} ${app.last_name}</h2>
                    <button class="modal-close" id="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="detail-scoring-row">
                        <div class="detail-scoring-card">
                            <div class="detail-temp-badge" style="background:${tempBadge.color}22; border:2px solid ${tempBadge.color}; border-radius:12px; padding:16px; text-align:center;">
                                <div style="font-size:2rem;">${tempBadge.emoji}</div>
                                <div style="font-weight:700; font-size:1.2rem; color:${tempBadge.color};">${tempBadge.label}</div>
                                <div style="font-size:1.8rem; font-weight:800; color:${tempBadge.color};">${sc.score || 0} / ${maxScore}</div>
                            </div>
                            <div style="margin-top:12px; display:flex; flex-direction:column; gap:6px; font-size:0.9rem;">
                                <div><strong>Персональный менеджер:</strong> ${sc.needs_personal_manager ? '✅ Да' : '❌ Нет'}</div>
                                <div><strong>Отдел:</strong> ${sc.recommended_department || '—'}</div>
                            </div>
                        </div>
                        <div class="detail-scoring-bars">
                            ${breakdownBars.map(b => {
                                const val = breakdown[b.key] || 0;
                                const pct = b.max > 0 ? (val / b.max) * 100 : 0;
                                return `
                                    <div class="scoring-bar-row">
                                        <span class="scoring-bar-label">${b.label}</span>
                                        <div class="scoring-bar-track">
                                            <div class="scoring-bar-fill" style="width:${pct}%; background:${tempBadge.color};"></div>
                                        </div>
                                        <span class="scoring-bar-value" style="color:${tempBadge.color};">${val}/${b.max}</span>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>

                    ${insights.length > 0 ? `
                    <div class="detail-section">
                        <h3>Инсайты</h3>
                        <ul class="insights-list">
                            ${insights.map(i => `<li>${i}</li>`).join('')}
                        </ul>
                    </div>` : ''}

                    <div class="detail-section">
                        <h3>Информация о клиенте</h3>
                        <div class="detail-grid">
                            <div><strong>Имя:</strong> ${app.first_name} ${app.middle_name || ''}</div>
                            <div><strong>Фамилия:</strong> ${app.last_name}</div>
                            <div><strong>Контакты:</strong> ${app.contact_data}</div>
                            <div><strong>Роль:</strong> ${app.role || '—'}</div>
                            <div><strong>Способ связи:</strong> ${app.preferred_contact_method || '—'}</div>
                            <div><strong>Удобное время:</strong> ${app.convenient_time || '—'}</div>
                        </div>
                    </div>

                    <div class="detail-section">
                        <h3>Информация о бизнесе</h3>
                        <div class="detail-grid">
                            <div><strong>Ниша:</strong> ${app.business_niche || '—'}</div>
                            <div><strong>Размер компании:</strong> ${app.company_size || '—'}</div>
                            <div><strong>Объём задачи:</strong> ${app.task_volume || '—'}</div>
                            <div><strong>Тип задачи:</strong> ${app.task_type || '—'}</div>
                            <div><strong>Продукт:</strong> ${app.product_interest || '—'}</div>
                            <div><strong>Бюджет:</strong> ${fmtBudget}</div>
                            <div><strong>Срок:</strong> ${app.project_deadline || '—'}</div>
                        </div>
                    </div>

                    ${app.business_info ? `<div class="detail-section"><h3>О бизнесе</h3><p>${app.business_info}</p></div>` : ''}
                    ${app.comment ? `<div class="detail-section"><h3>Комментарий клиента</h3><p>${app.comment}</p></div>` : ''}

                    <div class="detail-section">
                        <h3>Действия</h3>
                        <div class="actions-row">
                            <button type="button" class="btn btn-primary" id="btn-contact">📞 Связаться</button>
                            <div class="status-group">
                                <select id="status-select" class="form-select">
                                    ${this.statuses.map(s =>
                                        `<option value="${s}" ${app.status === s ? 'selected' : ''}>${s}</option>`
                                    ).join('')}
                                </select>
                                <button type="button" class="btn btn-secondary" id="btn-status">Изменить статус</button>
                            </div>
                        </div>
                    </div>

                    <div class="detail-section">
                        <h3>Заметки</h3>
                        <div id="notes-container" class="notes-list"></div>
                        <div class="note-input-row">
                            <textarea id="note-text" class="form-textarea" rows="2" placeholder="Введите заметку..."></textarea>
                            <button type="button" class="btn btn-primary" id="btn-note">Добавить</button>
                        </div>
                    </div>

                    <div class="detail-section">
                        <div class="detail-grid">
                            <div><strong>Создана:</strong> ${app.created_at || '—'}</div>
                            <div><strong>Статус:</strong> <span id="app-status-display">${app.status || 'Новая'}</span></div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" id="modal-close-btn">Закрыть</button>
                </div>
            </div>
        `;
    }

    bindEvents() {
        this.overlay.querySelectorAll('#modal-close, #modal-close-btn').forEach(el => {
            el.addEventListener('click', () => this.close());
        });
        this.overlay.addEventListener('click', (e) => { if (e.target === this.overlay) this.close(); });
        document.addEventListener('keydown', this._onEscape = (e) => { if (e.key === 'Escape') this.close(); });

        const btnContact = this.overlay.querySelector('#btn-contact');
        if (btnContact) btnContact.addEventListener('click', () => this.contact());

        const btnStatus = this.overlay.querySelector('#btn-status');
        const sel = this.overlay.querySelector('#status-select');
        if (btnStatus && sel) {
            btnStatus.addEventListener('click', () => this.changeStatus(sel.value));
        }

        const btnNote = this.overlay.querySelector('#btn-note');
        if (btnNote) btnNote.addEventListener('click', () => this.addNote());

        const noteText = this.overlay.querySelector('#note-text');
        if (noteText) {
            noteText.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.addNote();
                }
            });
        }

        this.renderNotes();
    }

    close() {
        if (this._onEscape) document.removeEventListener('keydown', this._onEscape);
        this.overlay.remove();
    }
}
