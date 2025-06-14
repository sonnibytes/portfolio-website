// AURA Portfolio - Updated Dashboard JavaScript for Unified Containers
// Compatible with the new unified-dashboard-container format
// File: static/projects/js/dashboard_panels.js

class UnifiedDashboardManager {
    constructor() {
        this.containers = new Map();
        this.animationObserver = null;
        this.init();
    }

    init() {
        this.initializeContainers();
        this.setupAnimationObserver();
        this.setupEventListeners();
        this.startAnimations();
        console.log('🚀 Unified Dashboard Manager initialized');
    }

    initializeContainers() {
        const containers = document.querySelectorAll('.unified-dashboard-container');
        containers.forEach(container => {
            const containerId = this.generateContainerId(container);
            const containerType = this.detectContainerType(container);
            
            this.containers.set(containerId, {
                element: container,
                type: containerType,
                color: this.getContainerColor(container),
                lastUpdate: Date.now()
            });

            // Initialize container-specific functionality
            this.initializeContainerType(container, containerType);
        });
        
        console.log(`Initialized ${this.containers.size} dashboard containers`);
    }

    generateContainerId(container) {
        const rect = container.getBoundingClientRect();
        const title = container.querySelector('.unified-container-title, h3, h4')?.textContent || 'container';
        return `container_${Math.round(rect.top)}_${title.replace(/\s+/g, '_').toLowerCase()}`;
    }

    detectContainerType(container) {
        // Detect container type based on content
        if (container.querySelector('.metric-content, .metric-value')) return 'metric';
        if (container.querySelector('.activity-feed, .activity-item')) return 'activity';
        if (container.querySelector('.featured-systems-grid')) return 'featured-systems';
        if (container.querySelector('.health-overview')) return 'health';
        if (container.querySelector('.tech-stack-overview')) return 'technology';
        if (container.querySelector('.chart-container')) return 'chart';
        if (container.querySelector('.alerts-container')) return 'alerts';
        if (container.querySelector('.quick-actions-grid')) return 'quick-actions';
        if (container.querySelector('.hero-content')) return 'hero';
        if (container.querySelector('.dev-status-overview')) return 'dev-status';
        return 'general';
    }

    getContainerColor(container) {
        const colorClasses = ['teal', 'lavender', 'coral', 'mint', 'yellow', 'navy', 'gunmetal'];
        for (const color of colorClasses) {
            if (container.classList.contains(color)) {
                return color;
            }
        }
        return 'teal'; // default
    }

    initializeContainerType(container, type) {
        switch (type) {
            case 'metric':
                this.initializeMetricContainer(container);
                break;
            case 'activity':
                this.initializeActivityContainer(container);
                break;
            case 'featured-systems':
                this.initializeFeaturedSystemsContainer(container);
                break;
            case 'health':
                this.initializeHealthContainer(container);
                break;
            case 'technology':
                this.initializeTechnologyContainer(container);
                break;
            case 'chart':
                this.initializeChartContainer(container);
                break;
            case 'alerts':
                this.initializeAlertsContainer(container);
                break;
            case 'quick-actions':
                this.initializeQuickActionsContainer(container);
                break;
            case 'hero':
                this.initializeHeroContainer(container);
                break;
            case 'dev-status':
                this.initializeDevStatusContainer(container);
                break;
        }
    }

    // ========== METRIC CONTAINERS ==========
    initializeMetricContainer(container) {
        const metricValues = container.querySelectorAll('[data-target], .metric-value');
        metricValues.forEach(value => {
            const target = parseFloat(value.dataset.target) || parseFloat(value.textContent) || 0;
            if (target > 0) {
                this.animateCounter(value, 0, target, 2000);
            }
        });

        // Add pulse animation to metric containers
        this.addMetricPulse(container);
    }

    animateCounter(element, start, end, duration, precision = 0) {
        const startTime = performance.now();
        const isDecimal = end % 1 !== 0 || precision > 0;
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function for smooth animation
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const current = start + (end - start) * easeOutQuart;
            
            if (isDecimal) {
                element.textContent = current.toFixed(precision);
            } else {
                element.textContent = Math.floor(current);
            }
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                element.textContent = isDecimal ? end.toFixed(precision) : Math.floor(end);
            }
        };
        
        requestAnimationFrame(animate);
    }

    addMetricPulse(container) {
        const metricValue = container.querySelector('.metric-value');
        if (metricValue) {
            setInterval(() => {
                metricValue.style.transform = 'scale(1.05)';
                setTimeout(() => {
                    metricValue.style.transform = 'scale(1)';
                }, 200);
            }, 5000); // Pulse every 5 seconds
        }
    }

    // ========== ACTIVITY CONTAINERS ==========
    initializeActivityContainer(container) {
        const activityFeed = container.querySelector('.activity-feed');
        if (activityFeed) {
            this.setupSmoothScrolling(activityFeed);
            this.animateActivityItems(container);
        }
    }

    setupSmoothScrolling(element) {
        element.style.scrollBehavior = 'smooth';
    }

    animateActivityItems(container) {
        const items = container.querySelectorAll('.activity-item');
        items.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                item.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                item.style.opacity = '1';
                item.style.transform = 'translateX(0)';
            }, index * 100);
        });
    }

    // ========== FEATURED SYSTEMS CONTAINERS ==========
    initializeFeaturedSystemsContainer(container) {
        const systemCards = container.querySelectorAll('.featured-system-card');
        systemCards.forEach((card, index) => {
            // Animate card entrance
            card.style.opacity = '0';
            card.style.transform = 'scale(0.9)';
            
            setTimeout(() => {
                card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'scale(1)';
            }, index * 150);

            // Initialize progress circles
            const progressCircle = card.querySelector('.system-progress');
            if (progressCircle) {
                this.animateProgressCircle(progressCircle);
            }
        });
    }

    animateProgressCircle(circle) {
        const progress = circle.style.getPropertyValue('--progress') || '0%';
        circle.style.setProperty('--progress', '0%');
        
        setTimeout(() => {
            circle.style.transition = '--progress 1.5s ease';
            circle.style.setProperty('--progress', progress);
        }, 500);
    }

    // ========== HEALTH CONTAINERS ==========
    initializeHealthContainer(container) {
        const healthDots = container.querySelectorAll('.health-metric-dot');
        healthDots.forEach((dot, index) => {
            setTimeout(() => {
                dot.style.animation = 'pulse 2s infinite';
            }, index * 200);
        });

        // Animate health status
        const healthStatus = container.querySelector('.health-status');
        if (healthStatus) {
            this.typeWriterEffect(healthStatus, healthStatus.textContent);
        }
    }

    typeWriterEffect(element, text) {
        element.textContent = '';
        let i = 0;
        const timer = setInterval(() => {
            element.textContent += text.charAt(i);
            i++;
            if (i > text.length - 1) {
                clearInterval(timer);
            }
        }, 50);
    }

    // ========== TECHNOLOGY CONTAINERS ==========
    initializeTechnologyContainer(container) {
        const usageBars = container.querySelectorAll('.usage-fill');
        usageBars.forEach((bar, index) => {
            const width = bar.style.width;
            bar.style.width = '0%';
            
            setTimeout(() => {
                bar.style.transition = 'width 1.5s ease';
                bar.style.width = width;
            }, index * 200 + 800); // Staggered animation
        });

        // Animate tech counts
        const techCounts = container.querySelectorAll('.tech-count');
        techCounts.forEach((count, index) => {
            const target = parseInt(count.textContent) || 0;
            setTimeout(() => {
                this.animateCounter(count, 0, target, 1000);
            }, index * 200);
        });
    }

    // ========== CHART CONTAINERS ==========
    initializeChartContainer(container) {
        const chartIcon = container.querySelector('.chart-icon .fas');
        if (chartIcon) {
            setInterval(() => {
                chartIcon.style.transform = 'rotate(360deg)';
                setTimeout(() => {
                    chartIcon.style.transform = 'rotate(0deg)';
                }, 1000);
            }, 10000); // Rotate every 10 seconds
        }

        this.setupChartControls(container);
    }

    setupChartControls(container) {
        const controls = container.querySelectorAll('.chart-control');
        controls.forEach(control => {
            control.addEventListener('click', (e) => {
                e.preventDefault();
                const action = control.dataset.action;
                this.handleChartAction(container, action);
            });
        });
    }

    handleChartAction(container, action) {
        console.log(`Chart action: ${action}`);
        // Add visual feedback
        const chartPlaceholder = container.querySelector('.chart-placeholder');
        if (chartPlaceholder) {
            chartPlaceholder.style.transform = 'scale(0.95)';
            setTimeout(() => {
                chartPlaceholder.style.transform = 'scale(1)';
            }, 150);
        }
    }

    // ========== ALERTS CONTAINERS ==========
    initializeAlertsContainer(container) {
        const alertItems = container.querySelectorAll('.alert-item');
        alertItems.forEach((alert, index) => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(10px)';
            
            setTimeout(() => {
                alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                alert.style.opacity = '1';
                alert.style.transform = 'translateY(0)';
            }, index * 150);
        });
    }

    // ========== QUICK ACTIONS CONTAINERS ==========
    initializeQuickActionsContainer(container) {
        const actionButtons = container.querySelectorAll('.quick-action');
        actionButtons.forEach((button, index) => {
            button.style.opacity = '0';
            button.style.transform = 'scale(0.8)';
            
            setTimeout(() => {
                button.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                button.style.opacity = '1';
                button.style.transform = 'scale(1)';
            }, index * 100);

            // Add hover sound effect (visual)
            button.addEventListener('mouseenter', () => {
                button.style.transform = 'scale(1.05)';
            });

            button.addEventListener('mouseleave', () => {
                button.style.transform = 'scale(1)';
            });
        });
    }

    // ========== HERO CONTAINERS ==========
    initializeHeroContainer(container) {
        const badges = container.querySelectorAll('.unified-featured-badge, .status-badge');
        badges.forEach((badge, index) => {
            badge.style.opacity = '0';
            badge.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                badge.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                badge.style.opacity = '1';
                badge.style.transform = 'translateY(0)';
            }, index * 200);
        });

        // Animate quick stats
        const quickStats = container.querySelectorAll('.quick-stat-value');
        quickStats.forEach((stat, index) => {
            const target = parseFloat(stat.textContent) || 0;
            setTimeout(() => {
                this.animateCounter(stat, 0, target, 2000, 1);
            }, 1000 + index * 300);
        });
    }

    // ========== DEV STATUS CONTAINERS ==========
    initializeDevStatusContainer(container) {
        const progressBars = container.querySelectorAll('.progress-fill');
        progressBars.forEach((bar, index) => {
            const width = bar.style.width;
            bar.style.width = '0%';
            
            setTimeout(() => {
                bar.style.transition = 'width 2s ease';
                bar.style.width = width;
            }, index * 300 + 500);
        });

        // Animate status values
        const statusValues = container.querySelectorAll('.status-value');
        statusValues.forEach((value, index) => {
            const target = parseInt(value.textContent.replace(/[^\d.]/g, '')) || 0;
            if (target > 0) {
                setTimeout(() => {
                    this.animateCounter(value, 0, target, 1500);
                }, index * 200);
            }
        });
    }

    // ========== ANIMATION OBSERVER ==========
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

        // Observe all containers
        this.containers.forEach(containerData => {
            this.animationObserver.observe(containerData.element);
        });
    }

    triggerEntranceAnimation(container) {
        const containerType = this.detectContainerType(container);
        
        // Apply entrance animation based on container type
        container.style.opacity = '1';
        container.style.transform = 'translateY(0)';
        
        // Different entrance effects for different types
        switch (containerType) {
            case 'metric':
                container.style.animation = 'fadeInUp 0.8s ease forwards';
                break;
            case 'hero':
                container.style.animation = 'fadeIn 1s ease forwards';
                break;
            case 'activity':
                container.style.animation = 'slideInLeft 0.6s ease forwards';
                break;
            default:
                container.style.animation = 'fadeInUp 0.6s ease forwards';
        }

        // Stop observing once animated
        this.animationObserver.unobserve(container);
    }

    // ========== EVENT LISTENERS ==========
    setupEventListeners() {
        // Container hover effects
        document.addEventListener('mouseenter', (e) => {
            const container = this.findClosestContainer(e.target);
            if (container) {
                this.handleContainerHover(container, true);
            }
        }, true);

        document.addEventListener('mouseleave', (e) => {
            const container = this.findClosestContainer(e.target);
            if (container) {
                this.handleContainerHover(container, false);
            }
        }, true);

        // Action link clicks
        document.addEventListener('click', (e) => {
            const actionLink = e.target.closest('.action-link');
            if (actionLink) {
                this.handleActionLinkClick(actionLink);
            }
        });
    }

    findClosestContainer(element) {
        if (!element || typeof element.closest !== 'function') return null;
        return element.closest('.unified-dashboard-container');
    }

    handleContainerHover(container, isEntering) {
        if (isEntering) {
            container.style.transform = 'translateY(-4px)';
            container.style.boxShadow = '0 12px 40px rgba(0, 0, 0, 0.4), 0 0 30px rgba(38, 198, 218, 0.2)';
        } else {
            container.style.transform = 'translateY(-3px)';
            container.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.3)';
        }
    }

    handleActionLinkClick(link) {
        // Add click animation
        link.style.transform = 'translateX(8px)';
        setTimeout(() => {
            link.style.transform = 'translateX(4px)';
        }, 150);
    }

    // ========== UTILITY METHODS ==========
    startAnimations() {
        // Start any continuous animations
        this.startGlobalAnimations();
    }

    startGlobalAnimations() {
        // Animate all progress circles on load
        setTimeout(() => {
            const progressCircles = document.querySelectorAll('.system-progress');
            progressCircles.forEach((circle, index) => {
                setTimeout(() => {
                    this.animateProgressCircle(circle);
                }, index * 200);
            });
        }, 1000);

        // Animate usage bars on load
        setTimeout(() => {
            const usageFills = document.querySelectorAll('.usage-fill');
            usageFills.forEach((fill, index) => {
                const width = fill.style.width;
                fill.style.width = '0%';
                setTimeout(() => {
                    fill.style.transition = 'width 1.5s ease';
                    fill.style.width = width;
                }, index * 150);
            });
        }, 1500);

        // Animate progress bars on load
        setTimeout(() => {
            const progressFills = document.querySelectorAll('.progress-fill');
            progressFills.forEach((fill, index) => {
                const width = fill.style.width;
                fill.style.width = '0%';
                setTimeout(() => {
                    fill.style.transition = 'width 2s ease';
                    fill.style.width = width;
                }, index * 200);
            });
        }, 2000);
    }

    // ========== PUBLIC API ==========
    refreshContainer(containerId) {
        const containerData = this.containers.get(containerId);
        if (containerData) {
            this.initializeContainerType(containerData.element, containerData.type);
        }
    }

    addContainer(container) {
        const containerId = this.generateContainerId(container);
        const containerType = this.detectContainerType(container);
        
        this.containers.set(containerId, {
            element: container,
            type: containerType,
            color: this.getContainerColor(container),
            lastUpdate: Date.now()
        });

        this.initializeContainerType(container, containerType);
    }
}

// ========== CSS ANIMATIONS ==========
const dashboardAnimations = `
<style>
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes fadeInUp {
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

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.8; transform: scale(1.05); }
}

/* Smooth transitions for all containers */
.unified-dashboard-container {
    transition: all 0.3s ease;
}

.metric-value {
    transition: transform 0.2s ease;
}

.system-progress {
    transition: all 0.3s ease;
}

.usage-fill {
    transition: width 1.5s ease;
}

.progress-fill {
    transition: width 2s ease;
}

.quick-action {
    transition: all 0.2s ease;
}

.action-link {
    transition: all 0.2s ease;
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
    .unified-dashboard-container,
    .unified-dashboard-container *,
    .unified-dashboard-container::before,
    .unified-dashboard-container::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
</style>
`;

// ========== INITIALIZATION ==========
document.addEventListener('DOMContentLoaded', () => {
    // Inject additional CSS
    document.head.insertAdjacentHTML('beforeend', dashboardAnimations);
    
    // Initialize unified dashboard manager
    window.unifiedDashboardManager = new UnifiedDashboardManager();
    
    console.log('🚀 AURA Unified Dashboard fully loaded and animated!');
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UnifiedDashboardManager;
}