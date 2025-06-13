// static/projects/js/dashboard_panels.js

class DashboardPanelManager {
    constructor() {
        this.panels = new Map();
        this.animationObserver = null;
        this.init();
    }

    init() {
        this.initializePanels();
        this.setupAnimationObserver();
        this.setupEventListeners();
        this.startRealtimeUpdates();
    }

    initializePanels() {
        const panels = document.querySelectorAll('.dashboard-panel');
        panels.forEach(panel => {
            const style = panel.dataset.panelStyle;
            const color = panel.dataset.panelColor;
            const panelId = this.generatePanelId(panel);
            
            this.panels.set(panelId, {
                element: panel,
                style: style,
                color: color,
                config: this.getPanelConfig(style),
                lastUpdate: Date.now()
            });

            // Initialize panel-specific functionality
            this.initializePanelType(panel, style);
        });
    }

    generatePanelId(panel) {
        // Generate unique ID based on panel position and content
        const rect = panel.getBoundingClientRect();
        const content = panel.textContent.slice(0, 20);
        return `panel_${Math.round(rect.top)}_${Math.round(rect.left)}_${content.replace(/\s+/g, '_')}`;
    }

    getPanelConfig(style) {
        const configs = {
            'dashboard': { updateInterval: 30000, animations: ['fade-in', 'slide-up'] },
            'metric': { updateInterval: 5000, animations: ['counter-up', 'glow'] },
            'activity': { updateInterval: 10000, animations: ['slide-in-left'] },
            'chart': { updateInterval: 15000, animations: ['fade-in', 'chart-draw'] },
            'alert': { updateInterval: 60000, animations: ['pulse', 'slide-down'] },
            'status': { updateInterval: 20000, animations: ['status-pulse'] },
            'component': { updateInterval: 0, animations: ['fade-in', 'scale-in'] },
            'grid': { updateInterval: 0, animations: ['fade-in'] }
        };
        return configs[style] || configs['dashboard'];
    }

    initializePanelType(panel, style) {
        switch (style) {
            case 'metric':
                this.initializeMetricPanel(panel);
                break;
            case 'chart':
                this.initializeChartPanel(panel);
                break;
            case 'activity':
                this.initializeActivityPanel(panel);
                break;
            case 'alert':
                this.initializeAlertPanel(panel);
                break;
            case 'status':
                this.initializeStatusPanel(panel);
                break;
        }
    }

    initializeMetricPanel(panel) {
        // Animate metric numbers
        const metricNumbers = panel.querySelectorAll('.metric-number[data-target]');
        metricNumbers.forEach(number => {
            const target = parseFloat(number.dataset.target) || 0;
            const precision = parseInt(panel.dataset.metricPrecision) || 0;
            this.animateCounter(number, 0, target, 2000, precision);
        });

        // Setup real-time updates for metrics
        if (panel.dataset.metricAnimate === 'true') {
            this.setupMetricUpdates(panel);
        }
    }

    initializeChartPanel(panel) {
        const chartCanvas = panel.querySelector('canvas');
        if (chartCanvas && panel.dataset.chartAnimate === 'true') {
            // Initialize chart controls
            this.setupChartControls(panel);
            
            // Setup chart refresh functionality
            this.setupChartRefresh(panel);
        }
    }

    initializeActivityPanel(panel) {
        if (panel.dataset.activityRealtime === 'true') {
            this.setupActivityRealtime(panel);
        }

        // Setup smooth scrolling for activity timeline
        const timeline = panel.querySelector('.activity-timeline');
        if (timeline) {
            this.setupSmoothScrolling(timeline);
        }
    }

    initializeAlertPanel(panel) {
        // Setup alert dismissal
        if (panel.dataset.alertDismissible === 'true') {
            this.setupAlertDismissal(panel);
        }

        // Setup alert level animations
        const level = panel.dataset.alertLevel;
        this.applyAlertAnimations(panel, level);
    }

    initializeStatusPanel(panel) {
        // Setup status indicator animations
        const statusDots = panel.querySelectorAll('.status-dot, .health-dot');
        statusDots.forEach(dot => {
            this.setupStatusAnimation(dot);
        });
    }

    setupAnimationObserver() {
        // Use Intersection Observer for entrance animations
        const options = {
            root: null,
            rootMargin: '0px',
            threshold: 0.1
        };

        this.animationObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.triggerEntranceAnimation(entry.target);
                }
            });
        }, options);

        // Observe all panels
        this.panels.forEach(panelData => {
            this.animationObserver.observe(panelData.element);
        });
    }

    triggerEntranceAnimation(panel) {
        const style = panel.dataset.panelStyle;
        const config = this.getPanelConfig(style);
        
        // Apply entrance animations based on panel type
        config.animations.forEach((animation, index) => {
            setTimeout(() => {
                panel.classList.add(`animate-${animation}`);
            }, index * 100);
        });

        // Stop observing once animated
        this.animationObserver.unobserve(panel);
    }

    setupEventListeners() {
        // Panel hover effects
        document.addEventListener('mouseenter', (e) => {
            if (e.target.closest('.dashboard-panel')) {
                this.handlePanelHover(e.target.closest('.dashboard-panel'), true);
            }
        }, true);

        document.addEventListener('mouseleave', (e) => {
            if (e.target.closest('.dashboard-panel')) {
                this.handlePanelHover(e.target.closest('.dashboard-panel'), false);
            }
        }, true);

        // Chart controls
        document.addEventListener('click', (e) => {
            if (e.target.closest('.chart-control')) {
                this.handleChartControl(e.target.closest('.chart-control'));
            }
        });

        // Alert dismissal
        document.addEventListener('click', (e) => {
            if (e.target.closest('.alert-dismiss')) {
                this.dismissAlert(e.target.closest('.dashboard-panel'));
            }
        });
    }

    handlePanelHover(panel, isEntering) {
        if (isEntering) {
            panel.classList.add('panel-hover');
            // Trigger hover-specific animations
            this.triggerHoverEffects(panel);
        } else {
            panel.classList.remove('panel-hover');
        }
    }

    triggerHoverEffects(panel) {
        const style = panel.dataset.panelStyle;
        
        // Add glow effect
        const glowEffect = panel.querySelector('.panel-glow-effect');
        if (glowEffect) {
            glowEffect.style.opacity = '0.3';
        }

        // Style-specific hover effects
        if (style === 'metric') {
            this.triggerMetricGlow(panel);
        } else if (style === 'status') {
            this.triggerStatusPulse(panel);
        }
    }

    animateCounter(element, start, end, duration, precision = 0) {
        const startTime = performance.now();
        const range = end - start;

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function for smooth animation
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const current = start + (range * easeOutQuart);
            
            element.textContent = current.toFixed(precision);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    setupChartControls(panel) {
        const controls = panel.querySelectorAll('.chart-control');
        controls.forEach(control => {
            const action = control.dataset.action;
            control.addEventListener('click', () => {
                this.handleChartAction(panel, action);
            });
        });
    }

    handleChartAction(panel, action) {
        const canvas = panel.querySelector('canvas');
        if (!canvas) return;

        // Get chart instance (assumes Chart.js)
        const chart = Chart.getChart(canvas);
        if (!chart) return;

        switch (action) {
            case 'zoom-in':
                if (chart.zoom) chart.zoom(1.1);
                break;
            case 'zoom-out':
                if (chart.zoom) chart.zoom(0.9);
                break;
            case 'reset':
                if (chart.resetZoom) chart.resetZoom();
                break;
        }

        // Visual feedback
        this.showControlFeedback(panel.querySelector(`[data-action="${action}"]`));
    }

    showControlFeedback(control) {
        control.classList.add('control-active');
        setTimeout(() => {
            control.classList.remove('control-active');
        }, 200);
    }

    setupAlertDismissal(panel) {
        const dismissButton = document.createElement('button');
        dismissButton.className = 'alert-dismiss';
        dismissButton.innerHTML = '<span class="material-icons">close</span>';
        dismissButton.setAttribute('aria-label', 'Dismiss alert');
        
        const header = panel.querySelector('.panel-header');
        if (header) {
            header.appendChild(dismissButton);
        }
    }

    dismissAlert(panel) {
        panel.classList.add('alert-dismissing');
        setTimeout(() => {
            panel.style.display = 'none';
            // Trigger layout adjustment for remaining panels
            this.adjustPanelLayout();
        }, 300);
    }

    setupMetricUpdates(panel) {
        const updateInterval = parseInt(panel.dataset.updateInterval) || 30000;
        
        setInterval(() => {
            this.updateMetricValues(panel);
        }, updateInterval);
    }

    updateMetricValues(panel) {
        // Show loading state
        this.showPanelLoading(panel);
        
        // Simulate API call (replace with actual endpoint)
        const panelId = Array.from(this.panels.keys()).find(key => 
            this.panels.get(key).element === panel
        );
        
        if (panelId) {
            this.fetchMetricData(panelId)
                .then(data => this.updatePanelData(panel, data))
                .catch(error => this.handleUpdateError(panel, error))
                .finally(() => this.hidePanelLoading(panel));
        }
    }

    async fetchMetricData(panelId) {
        // Mock API call - replace with actual implementation
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    timestamp: Date.now(),
                    metrics: {
                        cpu: Math.random() * 100,
                        memory: Math.random() * 100,
                        responseTime: Math.random() * 1000
                    }
                });
            }, 500);
        });
    }

    updatePanelData(panel, data) {
        const metricNumbers = panel.querySelectorAll('.metric-number[data-target]');
        
        // Update metric values with animation
        metricNumbers.forEach((number, index) => {
            const currentValue = parseFloat(number.textContent) || 0;
            const newValue = Object.values(data.metrics)[index] || currentValue;
            const precision = parseInt(panel.dataset.metricPrecision) || 0;
            
            // Update data-target for future reference
            number.dataset.target = newValue;
            
            // Animate to new value
            this.animateCounter(number, currentValue, newValue, 1000, precision);
        });

        // Update timestamp
        const timestamp = panel.querySelector('[data-timestamp="now"]');
        if (timestamp) {
            timestamp.textContent = 'just now';
        }
    }

    showPanelLoading(panel) {
        const loadingOverlay = panel.querySelector('.panel-loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'flex';
        }
    }

    hidePanelLoading(panel) {
        const loadingOverlay = panel.querySelector('.panel-loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }

    handleUpdateError(panel, error) {
        console.error('Panel update error:', error);
        
        // Show error state
        panel.classList.add('panel-error');
        setTimeout(() => {
            panel.classList.remove('panel-error');
        }, 3000);
    }

    setupActivityRealtime(panel) {
        const timeline = panel.querySelector('.activity-timeline');
        if (!timeline) return;

        // Setup WebSocket or polling for real-time updates
        const updateInterval = parseInt(panel.dataset.activityUpdateInterval) || 10000;
        
        setInterval(() => {
            this.fetchActivityUpdates(panel);
        }, updateInterval);
    }

    async fetchActivityUpdates(panel) {
        try {
            // Mock API call - replace with actual implementation
            const response = await fetch('/api/systems/activity/recent/');
            const activities = await response.json();
            
            this.updateActivityTimeline(panel, activities);
        } catch (error) {
            console.error('Failed to fetch activity updates:', error);
        }
    }

    updateActivityTimeline(panel, activities) {
        const timeline = panel.querySelector('.activity-timeline');
        const limit = parseInt(panel.dataset.activityLimit) || 10;
        
        // Clear existing activities
        timeline.innerHTML = '';
        
        // Add new activities with staggered animation
        activities.slice(0, limit).forEach((activity, index) => {
            const activityElement = this.createActivityElement(activity);
            activityElement.style.opacity = '0';
            activityElement.style.transform = 'translateX(-20px)';
            
            timeline.appendChild(activityElement);
            
            // Animate in
            setTimeout(() => {
                activityElement.style.opacity = '1';
                activityElement.style.transform = 'translateX(0)';
            }, index * 100);
        });
    }

    createActivityElement(activity) {
        const element = document.createElement('div');
        element.className = 'activity-item';
        element.style.transition = 'all 0.3s ease';
        
        element.innerHTML = `
            <div class="activity-timestamp">${this.formatTimestamp(activity.timestamp)}</div>
            <div class="activity-description">${activity.description}</div>
            <div class="activity-system">${activity.system}</div>
        `;
        
        return element;
    }

    formatTimestamp(timestamp) {
        const now = new Date();
        const activityTime = new Date(timestamp);
        const diffMs = now - activityTime;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffMins < 1) return 'just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        return `${diffDays}d ago`;
    }

    setupStatusAnimation(statusElement) {
        const status = statusElement.classList.contains('status-online') || 
                     statusElement.classList.contains('status-healthy') ? 'healthy' :
                     statusElement.classList.contains('status-warning') ? 'warning' :
                     statusElement.classList.contains('status-error') || 
                     statusElement.classList.contains('status-offline') ? 'error' : 'unknown';
        
        // Apply appropriate animation based on status
        switch (status) {
            case 'healthy':
                statusElement.style.animation = 'pulse-green 2s infinite';
                break;
            case 'warning':
                statusElement.style.animation = 'pulse-yellow 1.5s infinite';
                break;
            case 'error':
                statusElement.style.animation = 'pulse-red 1s infinite';
                break;
            default:
                statusElement.style.animation = 'pulse-gray 3s infinite';
        }
    }

    triggerMetricGlow(panel) {
        const metricNumbers = panel.querySelectorAll('.metric-number');
        metricNumbers.forEach(number => {
            number.classList.add('metric-glow');
            setTimeout(() => {
                number.classList.remove('metric-glow');
            }, 1000);
        });
    }

    triggerStatusPulse(panel) {
        const statusElements = panel.querySelectorAll('.status-dot, .health-dot');
        statusElements.forEach(element => {
            element.classList.add('status-highlight');
            setTimeout(() => {
                element.classList.remove('status-highlight');
            }, 800);
        });
    }

    applyAlertAnimations(panel, level) {
        panel.classList.add(`alert-${level}`);
        
        // Add pulsing effect for critical alerts
        if (level === 'error' || level === 'warning') {
            panel.classList.add('alert-pulse');
        }
    }

    adjustPanelLayout() {
        // Trigger CSS Grid or Flexbox reflow
        const container = document.querySelector('.dashboard-main-grid');
        if (container) {
            container.style.animation = 'none';
            container.offsetHeight; // Trigger reflow
            container.style.animation = 'layout-adjust 0.3s ease';
        }
    }

    setupSmoothScrolling(timeline) {
        let isScrolling = false;
        
        timeline.addEventListener('wheel', (e) => {
            if (isScrolling) return;
            
            e.preventDefault();
            isScrolling = true;
            
            const delta = e.deltaY;
            const scrollAmount = delta > 0 ? 100 : -100;
            
            timeline.scrollBy({
                top: scrollAmount,
                behavior: 'smooth'
            });
            
            setTimeout(() => {
                isScrolling = false;
            }, 150);
        });
    }

    startRealtimeUpdates() {
        // Setup global real-time update system
        this.panels.forEach((panelData, panelId) => {
            const { config, element } = panelData;
            
            if (config.updateInterval > 0) {
                setInterval(() => {
                    this.updatePanel(panelId);
                }, config.updateInterval);
            }
        });
    }

    async updatePanel(panelId) {
        const panelData = this.panels.get(panelId);
        if (!panelData) return;
        
        const { element, style } = panelData;
        
        try {
            // Show subtle loading indicator
            element.classList.add('panel-updating');
            
            // Fetch fresh data based on panel type
            const data = await this.fetchPanelData(panelId, style);
            
            // Update panel content
            this.updatePanelContent(element, data, style);
            
            // Update last update timestamp
            panelData.lastUpdate = Date.now();
            
        } catch (error) {
            this.handleUpdateError(element, error);
        } finally {
            element.classList.remove('panel-updating');
        }
    }

    async fetchPanelData(panelId, style) {
        // Mock implementation - replace with actual API calls
        const endpoints = {
            'metric': '/api/systems/metrics/',
            'status': '/api/systems/status/',
            'activity': '/api/systems/activity/',
            'chart': '/api/systems/performance/',
            'alert': '/api/systems/alerts/'
        };
        
        const endpoint = endpoints[style];
        if (!endpoint) return null;
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 200));
        
        // Return mock data
        return this.generateMockData(style);
    }

    generateMockData(style) {
        const mockData = {
            'metric': {
                cpu: Math.random() * 100,
                memory: Math.random() * 100,
                responseTime: Math.random() * 1000,
                timestamp: Date.now()
            },
            'status': {
                overall: Math.random() > 0.8 ? 'error' : Math.random() > 0.6 ? 'warning' : 'healthy',
                services: {
                    database: Math.random() > 0.9 ? 'error' : 'healthy',
                    api: Math.random() > 0.95 ? 'warning' : 'healthy',
                    cache: 'healthy'
                }
            },
            'activity': [
                {
                    id: Date.now(),
                    description: 'System performance optimized',
                    timestamp: Date.now() - Math.random() * 300000,
                    system: 'Core System'
                }
            ]
        };
        
        return mockData[style] || {};
    }

    updatePanelContent(element, data, style) {
        switch (style) {
            case 'metric':
                this.updateMetricPanelContent(element, data);
                break;
            case 'status':
                this.updateStatusPanelContent(element, data);
                break;
            case 'activity':
                this.updateActivityPanelContent(element, data);
                break;
        }
    }

    updateMetricPanelContent(element, data) {
        Object.keys(data).forEach(key => {
            if (key === 'timestamp') return;
            
            const metricElement = element.querySelector(`[data-metric="${key}"]`);
            if (metricElement) {
                const currentValue = parseFloat(metricElement.textContent) || 0;
                const newValue = data[key];
                this.animateCounter(metricElement, currentValue, newValue, 800);
            }
        });
    }

    updateStatusPanelContent(element, data) {
        // Update overall status
        const statusBadge = element.querySelector('.status-badge');
        if (statusBadge) {
            statusBadge.className = `status-badge status-${data.overall}`;
            statusBadge.textContent = data.overall.toUpperCase();
        }
        
        // Update service statuses
        Object.keys(data.services).forEach(service => {
            const serviceElement = element.querySelector(`[data-service="${service}"]`);
            if (serviceElement) {
                serviceElement.className = `health-dot status-${data.services[service]}`;
            }
        });
    }

    updateActivityPanelContent(element, activities) {
        this.updateActivityTimeline(element, activities);
    }

    // Cleanup method
    destroy() {
        if (this.animationObserver) {
            this.animationObserver.disconnect();
        }
        
        // Clear all intervals
        this.panels.forEach(panelData => {
            if (panelData.updateInterval) {
                clearInterval(panelData.updateInterval);
            }
        });
        
        this.panels.clear();
    }
}

// CSS animations for the JavaScript functionality
const additionalCSS = `
<style>
/* Animation keyframes */
@keyframes pulse-green {
    0%, 100% { box-shadow: 0 0 5px rgba(76, 175, 80, 0.7); }
    50% { box-shadow: 0 0 15px rgba(76, 175, 80, 1); }
}

@keyframes pulse-yellow {
    0%, 100% { box-shadow: 0 0 5px rgba(255, 193, 7, 0.7); }
    50% { box-shadow: 0 0 15px rgba(255, 193, 7, 1); }
}

@keyframes pulse-red {
    0%, 100% { box-shadow: 0 0 5px rgba(244, 67, 54, 0.7); }
    50% { box-shadow: 0 0 15px rgba(244, 67, 54, 1); }
}

@keyframes pulse-gray {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 1; }
}

@keyframes layout-adjust {
    0% { transform: scale(1.02); }
    100% { transform: scale(1); }
}

/* Panel state classes */
.panel-updating {
    position: relative;
}

.panel-updating::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--panel-accent), transparent);
    animation: loading-bar 1s infinite;
}

@keyframes loading-bar {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.panel-error {
    border-color: #f44336 !important;
    animation: error-shake 0.5s ease-in-out;
}

@keyframes error-shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}

.metric-glow {
    color: var(--panel-accent) !important;
    text-shadow: 0 0 10px var(--panel-accent);
    animation: metric-pulse 1s ease-in-out;
}

@keyframes metric-pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

.status-highlight {
    transform: scale(1.5);
    box-shadow: 0 0 10px currentColor;
    animation: status-bounce 0.8s ease-in-out;
}

@keyframes status-bounce {
    0%, 100% { transform: scale(1.5); }
    50% { transform: scale(1.8); }
}

.alert-pulse {
    animation: alert-urgency 2s infinite;
}

@keyframes alert-urgency {
    0%, 100% { background-color: var(--glass-bg); }
    50% { background-color: rgba(var(--panel-accent-rgb), 0.1); }
}

.alert-dismissing {
    animation: alert-dismiss 0.3s ease-out forwards;
}

@keyframes alert-dismiss {
    0% { 
        opacity: 1; 
        transform: translateX(0); 
    }
    100% { 
        opacity: 0; 
        transform: translateX(100%); 
    }
}

.control-active {
    background: var(--panel-accent) !important;
    color: white !important;
    transform: scale(0.95);
}

/* Entrance animations */
.animate-fade-in {
    animation: fadeIn 0.6s ease-out;
}

.animate-slide-up {
    animation: slideUp 0.8s ease-out;
}

.animate-slide-in-left {
    animation: slideInLeft 0.6s ease-out;
}

.animate-scale-in {
    animation: scaleIn 0.5s ease-out;
}

.animate-chart-draw {
    animation: chartDraw 1.2s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideUp {
    from { 
        opacity: 0; 
        transform: translateY(30px); 
    }
    to { 
        opacity: 1; 
        transform: translateY(0); 
    }
}

@keyframes slideInLeft {
    from { 
        opacity: 0; 
        transform: translateX(-30px); 
    }
    to { 
        opacity: 1; 
        transform: translateX(0); 
    }
}

@keyframes scaleIn {
    from { 
        opacity: 0; 
        transform: scale(0.8); 
    }
    to { 
        opacity: 1; 
        transform: scale(1); 
    }
}

@keyframes chartDraw {
    from { 
        opacity: 0; 
        transform: scale(0.9) rotateY(10deg); 
    }
    to { 
        opacity: 1; 
        transform: scale(1) rotateY(0deg); 
    }
}

/* Responsive animations */
@media (prefers-reduced-motion: reduce) {
    .dashboard-panel,
    .dashboard-panel *,
    .dashboard-panel::before,
    .dashboard-panel::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
</style>
`;

// Initialize the dashboard panel manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Inject additional CSS
    document.head.insertAdjacentHTML('beforeend', additionalCSS);
    
    // Initialize panel manager
    window.dashboardPanelManager = new DashboardPanelManager();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardPanelManager;
}