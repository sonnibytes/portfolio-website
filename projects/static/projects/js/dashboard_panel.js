// Fixed: static/projects/js/dashboard_panels.js

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
        this.startMetricAnimations();
    }

    initializePanels() {
        const panels = document.querySelectorAll('.dashboard-panel');
        panels.forEach(panel => {
            const style = panel.dataset.panelStyle || 'dashboard';
            const color = panel.dataset.panelColor || 'teal';
            const panelId = this.generatePanelId(panel);
            
            this.panels.set(panelId, {
                element: panel,
                style: style,
                color: color,
                lastUpdate: Date.now()
            });

            // Initialize panel-specific functionality
            this.initializePanelType(panel, style);
        });
    }

    generatePanelId(panel) {
        // Generate unique ID based on panel position and content
        const rect = panel.getBoundingClientRect();
        const title = panel.querySelector('.panel-title')?.textContent || 'panel';
        return `panel_${Math.round(rect.top)}_${title.replace(/\s+/g, '_')}`;
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
        // FIXED: Look for any element with data-target, not just .metric-number
        const metricNumbers = panel.querySelectorAll('[data-target]');
        metricNumbers.forEach(number => {
            const target = parseFloat(number.dataset.target) || 0;
            const precision = parseInt(panel.dataset.metricPrecision) || 0;
            this.animateCounter(number, 0, target, 2000, precision);
        });
    }

    initializeChartPanel(panel) {
        // Setup chart controls
        this.setupChartControls(panel);
    }

    initializeActivityPanel(panel) {
        const timeline = panel.querySelector('.activity-timeline');
        if (timeline) {
            this.setupSmoothScrolling(timeline);
        }
        
        // Update activity counter
        const counter = panel.querySelector('.activity-count');
        const activityItems = panel.querySelectorAll('.activity-item');
        if (counter) {
            counter.textContent = activityItems.length;
        }
    }

    initializeAlertPanel(panel) {
        if (panel.dataset.alertDismissible === 'true') {
            this.setupAlertDismissal(panel);
        }
    }

    initializeStatusPanel(panel) {
        const statusDots = panel.querySelectorAll('.status-dot, .health-dot');
        statusDots.forEach(dot => {
            this.setupStatusAnimation(dot);
        });
    }

    setupAnimationObserver() {
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
        const style = panel.dataset.panelStyle || 'dashboard';
        
        // Apply entrance animations based on panel type
        const animations = this.getAnimationsForStyle(style);
        
        animations.forEach((animation, index) => {
            setTimeout(() => {
                panel.classList.add(`animate-${animation}`);
            }, index * 100);
        });

        // Stop observing once animated
        this.animationObserver.unobserve(panel);
    }

    getAnimationsForStyle(style) {
        const animationMap = {
            'dashboard': ['fade-in', 'slide-up'],
            'grid': ['fade-in'],
            'activity': ['slide-in-left'],
            'component': ['fade-in', 'scale-in'],
            'chart': ['fade-in'],
            'alert': ['slide-up'],
            'metric': ['fade-in', 'scale-in'],
            'status': ['fade-in'],
        };
        
        return animationMap[style] || ['fade-in'];
    }

    setupEventListeners() {
        // FIXED: Panel hover effects with proper null checks
        document.addEventListener('mouseenter', (e) => {
            const panel = this.findClosestPanel(e.target);
            if (panel) {
                this.handlePanelHover(panel, true);
            }
        }, true);

        document.addEventListener('mouseleave', (e) => {
            const panel = this.findClosestPanel(e.target);
            if (panel) {
                this.handlePanelHover(panel, false);
            }
        }, true);

        // FIXED: Chart controls with proper null checks
        document.addEventListener('click', (e) => {
            const chartControl = this.findClosestChartControl(e.target);
            if (chartControl) {
                this.handleChartControl(chartControl);
            }
        });

        // FIXED: Alert dismissal with proper null checks
        document.addEventListener('click', (e) => {
            const alertDismiss = this.findClosestAlertDismiss(e.target);
            if (alertDismiss) {
                const panel = this.findClosestPanel(alertDismiss);
                if (panel) {
                    this.dismissAlert(panel);
                }
            }
        });
    }

    // FIXED: Helper methods to safely find closest elements
    findClosestPanel(element) {
        if (!element || typeof element.closest !== 'function') return null;
        return element.closest('.dashboard-panel');
    }

    findClosestChartControl(element) {
        if (!element || typeof element.closest !== 'function') return null;
        return element.closest('.chart-control');
    }

    findClosestAlertDismiss(element) {
        if (!element || typeof element.closest !== 'function') return null;
        return element.closest('.alert-dismiss');
    }

    handlePanelHover(panel, isEntering) {
        if (isEntering) {
            panel.classList.add('panel-hover');
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
            setTimeout(() => {
                glowEffect.style.opacity = '0';
            }, 1000);
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
        // Visual feedback
        this.showControlFeedback(panel.querySelector(`[data-action="${action}"]`));
        
        // You can add Chart.js integration here later
        console.log(`Chart action: ${action}`);
    }

    handleChartControl(control) {
        const action = control.dataset.action;
        const panel = this.findClosestPanel(control);
        
        if (panel) {
            this.handleChartAction(panel, action);
        }
    }

    showControlFeedback(control) {
        if (!control) return;
        
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
        dismissButton.style.cssText = `
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: rgba(255,255,255,0.1);
            border: none;
            border-radius: 50%;
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: rgba(255,255,255,0.7);
            cursor: pointer;
            transition: all 0.2s ease;
        `;
        
        dismissButton.addEventListener('mouseenter', () => {
            dismissButton.style.background = 'rgba(255,255,255,0.2)';
            dismissButton.style.color = 'rgba(255,255,255,1)';
        });
        
        dismissButton.addEventListener('mouseleave', () => {
            dismissButton.style.background = 'rgba(255,255,255,0.1)';
            dismissButton.style.color = 'rgba(255,255,255,0.7)';
        });
        
        panel.style.position = 'relative';
        panel.appendChild(dismissButton);
    }

    dismissAlert(panel) {
        panel.style.animation = 'alertDismiss 0.3s ease-out forwards';
        
        setTimeout(() => {
            panel.style.display = 'none';
            this.adjustPanelLayout();
        }, 300);
    }

    setupStatusAnimation(statusElement) {
        // Determine status type from classes
        let animationType = 'pulse-gray';
        
        if (statusElement.classList.contains('status-online') || 
            statusElement.classList.contains('status-healthy')) {
            animationType = 'pulse-green';
        } else if (statusElement.classList.contains('status-warning')) {
            animationType = 'pulse-yellow';
        } else if (statusElement.classList.contains('status-error') || 
                   statusElement.classList.contains('status-offline')) {
            animationType = 'pulse-red';
        }
        
        statusElement.style.animation = `${animationType} 2s infinite`;
    }

    triggerMetricGlow(panel) {
        const metricNumbers = panel.querySelectorAll('[data-target]');
        metricNumbers.forEach(number => {
            number.style.textShadow = '0 0 10px var(--panel-accent)';
            number.style.transform = 'scale(1.05)';
            
            setTimeout(() => {
                number.style.textShadow = '';
                number.style.transform = '';
            }, 1000);
        });
    }

    triggerStatusPulse(panel) {
        const statusElements = panel.querySelectorAll('.status-dot, .health-dot');
        statusElements.forEach(element => {
            element.style.transform = 'scale(1.5)';
            element.style.boxShadow = '0 0 10px currentColor';
            
            setTimeout(() => {
                element.style.transform = '';
                element.style.boxShadow = '';
            }, 800);
        });
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

    startMetricAnimations() {
        // Start all metric counter animations
        this.panels.forEach((panelData) => {
            if (panelData.style === 'metric') {
                this.initializeMetricPanel(panelData.element);
            }
        });
    }

    adjustPanelLayout() {
        // Trigger CSS Grid reflow
        const container = document.querySelector('.dashboard-main-grid');
        if (container) {
            container.style.animation = 'none';
            container.offsetHeight; // Trigger reflow
            container.style.animation = 'layout-adjust 0.3s ease';
        }
    }

    // Cleanup method
    destroy() {
        if (this.animationObserver) {
            this.animationObserver.disconnect();
        }
        this.panels.clear();
    }
}

// Add additional CSS animations
const additionalCSS = `
<style>
@keyframes alertDismiss {
    0% { 
        opacity: 1; 
        transform: translateX(0); 
    }
    100% { 
        opacity: 0; 
        transform: translateX(100%); 
    }
}

@keyframes layout-adjust {
    0% { transform: scale(1.02); }
    100% { transform: scale(1); }
}

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

/* Reduced motion support */
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

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Inject additional CSS
    document.head.insertAdjacentHTML('beforeend', additionalCSS);
    
    // Initialize panel manager
    window.dashboardPanelManager = new DashboardPanelManager();
    
    console.log('Dashboard Panel Manager initialized successfully');
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardPanelManager;
}