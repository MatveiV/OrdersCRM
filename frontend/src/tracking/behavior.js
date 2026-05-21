export class BehaviorTracker {
    constructor() {
        this.startTime = Date.now();
        this.buttonsClicked = [];
        this.hoverZones = new Set();
        this.currentZone = null;
        this.hoverTimeout = null;
        this.returnCount = this.getReturnCount();
        
        this.init();
    }

    init() {
        this.trackClicks();
        this.trackHover();
        this.trackScroll();
        this.incrementReturnCount();
    }

    getTimeSpent() {
        return Math.round((Date.now() - this.startTime) / 1000);
    }

    trackClicks() {
        document.addEventListener('click', (e) => {
            const target = e.target;
            const elementInfo = this.getElementInfo(target);
            this.buttonsClicked.push({
                element: elementInfo,
                timestamp: Date.now() - this.startTime
            });
        });
    }

    trackHover() {
        const zones = ['header', 'form', 'budget-slider', 'submit-button', 'footer'];
        
        zones.forEach(zone => {
            const element = document.querySelector(`[data-zone="${zone}"]`) || 
                           document.getElementById(zone === 'form' ? 'lead-form' : 
                           zone === 'header' ? 'animated-bg' :
                           zone === 'budget-slider' ? 'budget' :
                           zone === 'submit-button' ? 'lead-form' : null);
            
            if (element) {
                element.addEventListener('mouseenter', () => {
                    this.currentZone = zone;
                    this.hoverTimeout = setTimeout(() => {
                        this.hoverZones.add(zone);
                    }, 2000);
                });
                
                element.addEventListener('mouseleave', () => {
                    clearTimeout(this.hoverTimeout);
                    this.currentZone = null;
                });
            }
        });
    }

    trackScroll() {
        let maxScroll = 0;
        window.addEventListener('scroll', () => {
            const scrollPercent = Math.round((window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100);
            if (scrollPercent > maxScroll) {
                maxScroll = scrollPercent;
            }
        });
        
        this.getScrollDepth = () => maxScroll;
    }

    getReturnCount() {
        const count = sessionStorage.getItem('returnCount');
        return count ? parseInt(count) : 0;
    }

    incrementReturnCount() {
        this.returnCount++;
        sessionStorage.setItem('returnCount', this.returnCount);
    }

    getElementInfo(element) {
        const tag = element.tagName.toLowerCase();
        const id = element.id || '';
        const className = element.className || '';
        const text = element.textContent?.substring(0, 50) || '';
        return `${tag}${id ? '#' + id : ''}${className ? '.' + className.split(' ')[0] : ''}`;
    }

    getData() {
        return {
            time_spent_seconds: this.getTimeSpent(),
            buttons_clicked: JSON.stringify(this.buttonsClicked.map(b => b.element)),
            cursor_hover_zones: JSON.stringify([...this.hoverZones]),
            return_count: this.returnCount,
            page_views: this.returnCount,
            scroll_depth_percent: this.getScrollDepth ? this.getScrollDepth() : 0,
            device_type: this.getDeviceType(),
            browser: this.getBrowser(),
            os: this.getOS(),
            screen_resolution: `${window.screen.width}x${window.screen.height}`,
            user_agent: navigator.userAgent
        };
    }

    getDeviceType() {
        const width = window.innerWidth;
        if (width < 768) return 'mobile';
        if (width < 1024) return 'tablet';
        return 'desktop';
    }

    getBrowser() {
        const ua = navigator.userAgent;
        if (ua.includes('Chrome')) return 'Chrome';
        if (ua.includes('Firefox')) return 'Firefox';
        if (ua.includes('Safari')) return 'Safari';
        if (ua.includes('Edge')) return 'Edge';
        return 'Unknown';
    }

    getOS() {
        const ua = navigator.userAgent;
        if (ua.includes('Windows')) return 'Windows';
        if (ua.includes('Mac')) return 'macOS';
        if (ua.includes('Linux')) return 'Linux';
        if (ua.includes('Android')) return 'Android';
        if (ua.includes('iOS') || ua.includes('iPhone')) return 'iOS';
        return 'Unknown';
    }
}
