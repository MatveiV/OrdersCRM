const projectsData = [
    {
        name: 'Agent-SystemAnalyst_MemoryFrameworks',
        description: 'Фреймворки памяти для AI-агентов с краткосрочным и долгосрочным контекстом',
        stack: ['Python', 'LLM', 'LangChain', 'Vector DB'],
        category: 'ai',
        github: 'https://github.com/MatveiV'
    },
    {
        name: 'Znaika_Neznaika_bot',
        description: 'Образовательный Telegram-бот с игровыми механиками обучения',
        stack: ['Python', 'aiogram', 'SQLite'],
        category: 'ai',
        github: 'https://github.com/MatveiV'
    },
    {
        name: 'MultiTools AI Agent Bot',
        description: 'Мультифункциональный AI-бот с набором инструментов для автоматизации',
        stack: ['Python', 'OpenAI API', 'Telegram API'],
        category: 'ai',
        github: 'https://github.com/MatveiV'
    },
    {
        name: 'ShortLongMemory Bots',
        description: 'Боты с гибридной памятью: краткосрочная + долгосрочная контекстная память',
        stack: ['Python', 'LLM', 'Redis', 'PostgreSQL'],
        category: 'ai',
        github: 'https://github.com/MatveiV'
    },
    {
        name: 'Product MCP Bot',
        description: 'Telegram-бот с поддержкой Model Context Protocol для интеграции с внешними системами',
        stack: ['Python', 'MCP', 'FastAPI'],
        category: 'ai',
        github: 'https://github.com/MatveiV'
    },
    {
        name: 'AI Client PDF Generator',
        description: 'Генератор PDF-отчётов на основе AI-анализа клиентских данных',
        stack: ['Python', 'LLM', 'ReportLab', 'Pandas'],
        category: 'ai',
        github: 'https://github.com/MatveiV'
    },
    {
        name: 'RAG-Agent',
        description: 'RAG-агент для поиска и генерации ответов на основе корпоративной базы знаний',
        stack: ['Python', 'LangChain', 'ChromaDB', 'OpenAI'],
        category: 'ai',
        github: 'https://github.com/MatveiV'
    },
    {
        name: 'Team Assistant Telegram Bot',
        description: 'Командный ассистент для управления задачами и коммуникацией в Telegram',
        stack: ['Python', 'aiogram', 'PostgreSQL'],
        category: 'ai',
        github: 'https://github.com/MatveiV'
    },
    {
        name: 'Refactoring_MV',
        description: 'Рефакторинг монолита с Python на Go для повышения производительности',
        stack: ['Go', 'Python', 'gRPC', 'Docker'],
        category: 'infra',
        github: 'https://github.com/MatveiV'
    },
    {
        name: 'Loki-Grafana',
        description: 'Система мониторинга и логирования на базе Loki + Grafana',
        stack: ['Loki', 'Grafana', 'Docker', 'Promtail'],
        category: 'infra',
        github: 'https://github.com/MatveiV'
    },
    {
        name: 'CoinParser',
        description: 'Парсер и анализатор криптовалютных данных с визуализацией',
        stack: ['Python', 'BeautifulSoup', 'Pandas', 'Plotly'],
        category: 'infra',
        github: 'https://github.com/MatveiV'
    },
    {
        name: 'MiniCRM',
        description: 'Лёгкая CRM-система для управления лидами и клиентами',
        stack: ['Python', 'FastAPI', 'PostgreSQL', 'Docker'],
        category: 'infra',
        github: 'https://github.com/MatveiV'
    },
    {
        name: 'ML_Fin_Notebooks',
        description: 'Бэктестинг финансовых стратегий: LSTM, TFT, классические ML-модели',
        stack: ['Python', 'TensorFlow', 'PyTorch', 'Pandas'],
        category: 'ml',
        github: 'https://github.com/MatveiV'
    }
];

export function renderProjects(filter = 'all') {
    const grid = document.getElementById('projects-grid');
    if (!grid) return;
    
    grid.innerHTML = '';
    
    const filtered = filter === 'all' ? projectsData : projectsData.filter(p => p.category === filter);
    
    filtered.forEach(project => {
        const card = document.createElement('div');
        card.classList.add('project-card');
        card.innerHTML = `
            <h3 class="project-name">${project.name}</h3>
            <p class="project-desc">${project.description}</p>
            <div class="project-stack">
                ${project.stack.map(tech => `<span class="tech-badge">${tech}</span>`).join('')}
            </div>
            <a href="${project.github}" target="_blank" rel="noopener" class="project-link">GitHub →</a>
        `;
        grid.appendChild(card);
    });
}

export function initProjectFilters() {
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            renderProjects(tab.dataset.filter);
        });
    });
}
