const API_BASE = '/api';

let timeOnPage = 0;
let buttonsClicked = {};
let cursorPositions = [];
let returnFrequency = 0;
let intervalId = null;

function getElementIdentifier(el) {
    if (el.getAttribute && el.getAttribute('data-metric-id')) {
        return el.getAttribute('data-metric-id');
    }
    if (el.id) return el.id;
    if (el.name) return el.name;
    if (el.textContent) return el.textContent.trim().slice(0, 30);
    return el.tagName.toLowerCase();
}

async function sendMetrics() {
    timeOnPage += 1;
    const posJson = JSON.stringify(cursorPositions);
    const btnJson = JSON.stringify(buttonsClicked);

    const payload = {
        application_id: 0,
        time_on_page: timeOnPage,
        buttons_clicked: btnJson,
        cursor_positions: posJson,
        return_frequency: returnFrequency,
    };

    try {
        await fetch(`${API_BASE}/behavior-metrics/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
    } catch (err) {
        console.warn('Metrics send failed:', err);
    }

    cursorPositions = [];
}

function sendFinalMetrics() {
    if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
    }
    timeOnPage += 1;
    const posJson = JSON.stringify(cursorPositions);
    const btnJson = JSON.stringify(buttonsClicked);

    const payload = JSON.stringify({
        application_id: 0,
        time_on_page: timeOnPage,
        buttons_clicked: btnJson,
        cursor_positions: posJson,
        return_frequency: returnFrequency,
    });

    try {
        navigator.sendBeacon(`${API_BASE}/behavior-metrics/`, payload);
    } catch (err) {
        console.warn('Final metrics sendBeacon failed:', err);
    }
}

function initMetrics() {
    returnFrequency = parseInt(localStorage.getItem('bm_return_count') || '0', 10);
    localStorage.setItem('bm_return_count', String(returnFrequency + 1));

    document.addEventListener('mousemove', (e) => {
        cursorPositions.push({ x: e.clientX, y: e.clientY });
    });

    document.addEventListener('click', (e) => {
        const el = e.target.closest('button, a, .project-card, .filter-tab, .cta-button, .submit-btn, input, select, textarea, label, [data-metric-id]');
        if (el) {
            const id = getElementIdentifier(el);
            buttonsClicked[id] = (buttonsClicked[id] || 0) + 1;
        }
    });

    intervalId = setInterval(sendMetrics, 1000);

    window.addEventListener('beforeunload', sendFinalMetrics);
    window.addEventListener('pagehide', sendFinalMetrics);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMetrics);
} else {
    initMetrics();
}
