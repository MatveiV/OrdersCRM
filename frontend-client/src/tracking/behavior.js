export class BehaviorTracker {
    constructor() {
        this.startTime = Date.now();
        this.buttonsClicked = [];
        this.cursorHoverZones = new Set();
        this.returnCount = this.getReturnCount();
        
        this.initTracking();
    }
    
    initTracking() {
        document.addEventListener('click', (e) => {
            const target = e.target.closest('button, a, .project-card, .filter-tab, .cta-button, .submit-btn, input, select, textarea');
            if (target) {
                const id = target.id || target.className || target.tagName;
                this.buttonsClicked.push({ element: id, timestamp: Date.now() - this.startTime });
            }
        });
        
        document.querySelectorAll('.hero-section, .projects-section, .form-section, .project-card').forEach(zone => {
            zone.addEventListener('mouseenter', () => {
                this.cursorHoverZones.add(zone.id || zone.className);
            });
        });
        
        window.addEventListener('beforeunload', () => {
            localStorage.setItem('orderscrm_return_count', this.returnCount + 1);
        });
    }
    
    getReturnCount() {
        return parseInt(localStorage.getItem('orderscrm_return_count') || '0');
    }
    
    getData() {
        return {
            time_spent_seconds: Math.round((Date.now() - this.startTime) / 1000),
            buttons_clicked: this.buttonsClicked,
            cursor_hover_zones: Array.from(this.cursorHoverZones),
            return_count: this.returnCount
        };
    }
}
