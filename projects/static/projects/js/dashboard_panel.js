// AURA Portfolio - Enhanced Dashboard JavaScript for Learning Focus
// Compatible with unified containers + learning-specific animations
// File: static/projects/js/dashboard_panels.js

class UnifiedDashboardManager {
    constructor() {
        this.containers = new Map();
        this.animationObserver = null;
        this.learningAnimations = new Map(); // New: Learning-specific animations
        this.init();
    }

    init() {
        this.initializeContainers();
        this.setupAnimationObserver();
        this.setupEventListeners();
        this.initializeLearningAnimations(); // New: Learning-specific setup
        this.startAnimations();
        console.log('🚀 Unified Dashboard Manager initialized with learning support');
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
        // Detect container type based on content (enhanced for learning)
        if (container.querySelector('.metric-content, .metric-value')) return 'metric';
        if (container.querySelector('.chart-container, #learningStagesChart')) return 'chart';
        if (container.querySelector('.system-card, .learning-system-card')) return 'grid';
        if (container.querySelector('.activity-item, .timeline-event')) return 'activity';
        if (container.querySelector('.skills-pills, .skill-pill')) return 'skills'; // New
        if (container.querySelector('.learning-metric-card')) return 'learning'; // New
        if (container.querySelector('.assessment-criteria')) return 'assessment'; // New
        if (container.querySelector('.datalog-item')) return 'datalogs';
        if (container.querySelector('.tech-analysis-card')) return 'tech';
        if (container.querySelector('.alert')) return 'alert';
        if (container.querySelector('.status-indicator')) return 'status';
        return 'dashboard';
    }

    getContainerColor(container) {
        // Extract color from classes (enhanced for learning stages)
        const classList = Array.from(container.classList);
        const colorClasses = ['teal', 'purple', 'coral', 'lavender', 'mint', 'yellow', 'navy', 'gunmetal'];
        const learningStageClasses = ['tutorial', 'guided', 'independent', 'refactoring', 'contributing', 'teaching'];
        
        // Check for standard colors first
        for (const color of colorClasses) {
            if (classList.includes(color)) return color;
        }
        
        // Check for learning stage colors
        for (const stage of learningStageClasses) {
            if (classList.some(cls => cls.includes(stage))) {
                return this.getLearningStageColor(stage);
            }
        }
        
        return 'teal'; // default
    }

    getLearningStageColor(stage) {
        const stageColors = {
            'tutorial': 'yellow',
            'guided': 'mint',
            'independent': 'teal',
            'refactoring': 'purple',
            'contributing': 'coral',
            'teaching': 'yellow'
        };
        return stageColors[stage] || 'teal';
    }

    initializeContainerType(container, type) {
        switch (type) {
            case 'metric':
                this.initializeMetricContainer(container);
                break;
            case 'chart':
                this.initializeChartContainer(container);
                break;
            case 'grid':
                this.initializeGridContainer(container);
                break;
            case 'activity':
                this.initializeActivityContainer(container);
                break;
            case 'skills': // New
                this.initializeSkillsContainer(container);
                break;
            case 'learning': // New
                this.initializeLearningContainer(container);
                break;
            case 'assessment': // New
                this.initializeAssessmentContainer(container);
                break;
            case 'alert':
                this.initializeAlertContainer(container);
                break;
            case 'status':
                this.initializeStatusContainer(container);
                break;
            default:
                this.initializeDashboardContainer(container);
        }
    }

    // ========== NEW: LEARNING-SPECIFIC CONTAINER INITIALIZERS ==========

    initializeSkillsContainer(container) {
        const skillPills = container.querySelectorAll('.skill-pill');
        
        // Staggered entrance animation for skill pills
        skillPills.forEach((pill, index) => {
            pill.style.opacity = '0';
            pill.style.transform = 'translateY(10px) scale(0.9)';
            pill.style.transition = 'all 0.4s ease';
            
            setTimeout(() => {
                pill.style.opacity = '1';
                pill.style.transform = 'translateY(0) scale(1)';
            }, index * 100);
        });

        // Hover effects for skill pills
        skillPills.forEach(pill => {
            pill.addEventListener('mouseenter', () => {
                pill.style.transform = 'translateY(-2px) scale(1.05)';
                pill.style.boxShadow = '0 4px 12px rgba(100, 181, 246, 0.3)';
            });
            
            pill.addEventListener('mouseleave', () => {
                pill.style.transform = 'translateY(0) scale(1)';
                pill.style.boxShadow = '';
            });
        });
    }

    initializeLearningContainer(container) {
        const learningCards = container.querySelectorAll('.learning-metric-card');
        const progressBars = container.querySelectorAll('.progress-fill');
        const learningBadges = container.querySelectorAll('.learning-stage-badge, .portfolio-ready-indicator');

        // Animate learning metric cards
        learningCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'all 0.6s ease';
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 150);

            // Hover effect
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-4px) scale(1.02)';
                card.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.15)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) scale(1)';
                card.style.boxShadow = '';
            });
        });

        // Animate learning progress bars
        setTimeout(() => {
            progressBars.forEach(bar => {
                const targetWidth = bar.style.width || '0%';
                bar.style.width = '0%';
                bar.style.transition = 'width 1.5s ease-out';
                
                setTimeout(() => {
                    bar.style.width = targetWidth;
                }, 100);
            });
        }, 500);

        // Animate learning badges
        learningBadges.forEach((badge, index) => {
            badge.style.opacity = '0';
            badge.style.transform = 'scale(0.8)';
            badge.style.transition = 'all 0.5s ease';
            
            setTimeout(() => {
                badge.style.opacity = '1';
                badge.style.transform = 'scale(1)';
            }, 200 + (index * 100));
        });
    }

    initializeAssessmentContainer(container) {
        const criteriaItems = container.querySelectorAll('.criteria-item');
        const recommendationCards = container.querySelectorAll('.recommendation-card');

        // Animate assessment criteria
        criteriaItems.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateX(-20px)';
            item.style.transition = 'all 0.5s ease';
            
            setTimeout(() => {
                item.style.opacity = '1';
                item.style.transform = 'translateX(0)';
            }, index * 100);

            // Hover effects
            item.addEventListener('mouseenter', () => {
                item.style.transform = 'translateX(5px)';
                item.style.background = 'rgba(255, 255, 255, 0.08)';
            });
            
            item.addEventListener('mouseleave', () => {
                item.style.transform = 'translateX(0)';
                item.style.background = 'rgba(255, 255, 255, 0.05)';
            });
        });

        // Animate recommendation cards
        recommendationCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(15px)';
            card.style.transition = 'all 0.4s ease';
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 300 + (index * 150));
        });
    }

    // ========== ENHANCED EXISTING INITIALIZERS ==========

    initializeMetricContainer(container) {
        const metricValues = container.querySelectorAll('.metric-value, .metric-value-large');
        const progressBars = container.querySelectorAll('.progress-fill, .usage-fill');

        // Animate metric values with count-up effect
        metricValues.forEach(metric => {
            const target = parseInt(metric.dataset.target || metric.textContent.replace(/[^\d]/g, ''));
            if (target && target > 0) {
                this.animateCountUp(metric, 0, target, 1500);
            }
        });

        // Animate progress bars
        setTimeout(() => {
            progressBars.forEach(bar => {
                const targetWidth = bar.style.width || bar.dataset.width || '0%';
                bar.style.width = '0%';
                bar.style.transition = 'width 2s ease-out';
                
                setTimeout(() => {
                    bar.style.width = targetWidth;
                }, 200);
            });
        }, 500);
    }

    initializeActivityContainer(container) {
        const activityItems = container.querySelectorAll('.activity-item, .timeline-event');
        const timelineEvents = container.querySelectorAll('.timeline-event');

        // Enhanced timeline animations for learning events
        if (timelineEvents.length > 0) {
            timelineEvents.forEach((event, index) => {
                event.style.opacity = '0';
                event.style.transform = 'translateX(-30px)';
                event.style.transition = 'all 0.6s ease';
                
                setTimeout(() => {
                    event.style.opacity = '1';
                    event.style.transform = 'translateX(0)';
                }, index * 200);

                // Learning milestone specific animations
                const icon = event.querySelector('.timeline-icon');
                if (icon) {
                    setTimeout(() => {
                        icon.style.animation = 'pulse 0.6s ease-in-out';
                    }, index * 200 + 300);
                }
            });
        } else {
            // Standard activity items
            activityItems.forEach((item, index) => {
                item.style.opacity = '0';
                item.style.transform = 'translateY(20px)';
                item.style.transition = 'all 0.5s ease';
                
                setTimeout(() => {
                    item.style.opacity = '1';
                    item.style.transform = 'translateY(0)';
                }, index * 100);
            });
        }
    }

    initializeGridContainer(container) {
        const gridItems = container.querySelectorAll('.system-card, .learning-system-card, .tech-analysis-card');
        
        gridItems.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(30px) scale(0.95)';
            item.style.transition = 'all 0.6s ease';
            
            setTimeout(() => {
                item.style.opacity = '1';
                item.style.transform = 'translateY(0) scale(1)';
            }, index * 100);

            // Enhanced hover effects for learning cards
            if (item.classList.contains('learning-system-card')) {
                item.addEventListener('mouseenter', () => {
                    item.style.transform = 'translateY(-8px) scale(1.02)';
                    item.style.boxShadow = '0 12px 40px rgba(0, 0, 0, 0.15)';
                });
                
                item.addEventListener('mouseleave', () => {
                    item.style.transform = 'translateY(0) scale(1)';
                    item.style.boxShadow = '';
                });
            }
        });
    }

    // ========== NEW: LEARNING-SPECIFIC ANIMATIONS ==========

    initializeLearningAnimations() {
        // Learning stage badge animations
        this.setupLearningStageAnimations();
        
        // Skill progression animations
        this.setupSkillProgressionAnimations();
        
        // Portfolio readiness animations
        this.setupPortfolioReadinessAnimations();
        
        // Learning velocity animations
        this.setupLearningVelocityAnimations();
    }

    setupLearningStageAnimations() {
        const stageBadges = document.querySelectorAll('.learning-stage-badge');
        
        stageBadges.forEach(badge => {
            // Add stage-specific glow effects
            const stage = Array.from(badge.classList).find(cls => cls.startsWith('learning-stage-'));
            if (stage) {
                badge.addEventListener('mouseenter', () => {
                    badge.style.boxShadow = this.getLearningStageGlow(stage);
                    badge.style.transform = 'scale(1.05)';
                });
                
                badge.addEventListener('mouseleave', () => {
                    badge.style.boxShadow = '';
                    badge.style.transform = 'scale(1)';
                });
            }
        });
    }

    setupSkillProgressionAnimations() {
        const skillItems = document.querySelectorAll('.skill-progression-item');
        
        skillItems.forEach((item, index) => {
            // Intersection observer for skill items
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateX(0)';
                        
                        // Animate mastery level badge
                        const masteryBadge = entry.target.querySelector('.mastery-level');
                        if (masteryBadge) {
                            setTimeout(() => {
                                masteryBadge.style.animation = 'pulse 0.5s ease-in-out';
                            }, 300);
                        }
                    }
                });
            }, { threshold: 0.1 });
            
            item.style.opacity = '0';
            item.style.transform = 'translateX(-20px)';
            item.style.transition = 'all 0.6s ease';
            
            observer.observe(item);
        });
    }

    setupPortfolioReadinessAnimations() {
        const readinessIndicators = document.querySelectorAll('.portfolio-ready-indicator');
        
        readinessIndicators.forEach(indicator => {
            if (indicator.classList.contains('portfolio-ready-yes')) {
                // Add success glow for portfolio-ready items
                indicator.addEventListener('mouseenter', () => {
                    indicator.style.boxShadow = '0 0 15px rgba(76, 175, 80, 0.4)';
                });
                
                indicator.addEventListener('mouseleave', () => {
                    indicator.style.boxShadow = '';
                });
            }
        });
    }

    setupLearningVelocityAnimations() {
        const velocityElements = document.querySelectorAll('[data-learning-velocity]');
        
        velocityElements.forEach(element => {
            const velocity = parseFloat(element.dataset.learningVelocity);
            
            // Add velocity-based animation speed
            if (velocity > 2) {
                element.style.animation = 'pulse 1s ease-in-out infinite';
            } else if (velocity > 1) {
                element.style.animation = 'pulse 2s ease-in-out infinite';
            }
        });
    }

    getLearningStageGlow(stageClass) {
        const glowColors = {
            'learning-stage-tutorial': '0 0 20px rgba(255, 183, 77, 0.6)',
            'learning-stage-guided': '0 0 20px rgba(129, 199, 132, 0.6)',
            'learning-stage-independent': '0 0 20px rgba(100, 181, 246, 0.6)',
            'learning-stage-refactoring': '0 0 20px rgba(186, 104, 200, 0.6)',
            'learning-stage-contributing': '0 0 20px rgba(79, 195, 247, 0.6)',
            'learning-stage-teaching': '0 0 20px rgba(255, 213, 79, 0.6)'
        };
        return glowColors[stageClass] || '0 0 20px rgba(100, 181, 246, 0.6)';
    }

    // ========== ENHANCED EXISTING METHODS ==========

    animateCountUp(element, start, end, duration) {
        const startTime = performance.now();
        const range = end - start;
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function for smooth animation
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const current = Math.floor(start + (range * easeOutQuart));
            
            // Preserve original formatting (%, h, etc.)
            const originalText = element.textContent;
            const suffix = originalText.replace(/[\d,]/g, '').trim();
            element.textContent = current.toLocaleString() + (suffix ? ' ' + suffix : '');
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    setupAnimationObserver() {
        this.animationObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const container = entry.target;
                    const containerId = this.generateContainerId(container);
                    const containerData = this.containers.get(containerId);
                    
                    if (containerData && !container.dataset.animated) {
                        this.animateContainer(container, containerData.type);
                        container.dataset.animated = 'true';
                    }
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -10% 0px'
        });

        // Observe all containers
        this.containers.forEach(data => {
            this.animationObserver.observe(data.element);
        });
    }

    animateContainer(container, type) {
        container.style.opacity = '0';
        container.style.transform = 'translateY(30px)';
        container.style.transition = 'all 0.8s ease-out';
        
        setTimeout(() => {
            container.style.opacity = '1';
            container.style.transform = 'translateY(0)';
        }, 100);
    }

    setupEventListeners() {
        // Enhanced hover effects for learning elements
        document.addEventListener('mouseenter', (e) => {
            if (e.target.matches('.skill-pill, .learning-stage-badge, .mastery-level')) {
                e.target.style.transition = 'all 0.2s ease';
            }
        }, true);

        // Learning card interactions
        document.addEventListener('click', (e) => {
            if (e.target.matches('.learning-metric-card, .skill-progression-item')) {
                // Add click ripple effect
                this.addRippleEffect(e.target, e);
            }
        });
    }

    addRippleEffect(element, event) {
        const ripple = document.createElement('div');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            pointer-events: none;
            transform: scale(0);
            animation: ripple 0.6s ease-out;
        `;
        
        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }

    startAnimations() {
        // Initialize all containers that are already visible
        setTimeout(() => {
            this.containers.forEach((data, id) => {
                const rect = data.element.getBoundingClientRect();
                if (rect.top < window.innerHeight && rect.bottom > 0) {
                    if (!data.element.dataset.animated) {
                        this.animateContainer(data.element, data.type);
                        data.element.dataset.animated = 'true';
                    }
                }
            });
        }, 100);
    }

    // ========== EXISTING METHODS (UNCHANGED) ==========
    
    initializeDashboardContainer(container) {
        // Keep existing implementation
        container.style.opacity = '0';
        container.style.transform = 'translateY(20px)';
        setTimeout(() => {
            container.style.opacity = '1';
            container.style.transform = 'translateY(0)';
            container.style.transition = 'all 0.6s ease';
        }, 100);
    }

    initializeChartContainer(container) {
        // Keep existing implementation
        const chartElements = container.querySelectorAll('canvas, .chart-placeholder');
        chartElements.forEach(chart => {
            chart.style.opacity = '0';
            chart.style.transform = 'scale(0.9)';
            chart.style.transition = 'all 0.8s ease';
            
            setTimeout(() => {
                chart.style.opacity = '1';
                chart.style.transform = 'scale(1)';
            }, 300);
        });
    }

    initializeAlertContainer(container) {
        // Keep existing implementation with enhanced learning alerts
        const dismissBtn = container.querySelector('.alert-dismiss');
        if (dismissBtn) {
            dismissBtn.addEventListener('click', () => {
                container.style.transform = 'translateX(100%)';
                container.style.opacity = '0';
                setTimeout(() => container.remove(), 300);
            });
        }
    }

    initializeStatusContainer(container) {
        // Keep existing implementation
        const statusIndicators = container.querySelectorAll('.status-indicator');
        statusIndicators.forEach(indicator => {
            const status = indicator.dataset.status;
            if (status === 'active' || status === 'portfolio-ready') {
                indicator.style.animation = 'pulse 2s ease-in-out infinite';
            }
        });
    }
}

// ========== ENHANCED CSS ANIMATIONS FOR LEARNING ==========
const enhancedDashboardAnimations = `
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

@keyframes ripple {
    from { transform: scale(0); opacity: 0.6; }
    to { transform: scale(1); opacity: 0; }
}

@keyframes skillPillGlow {
    0%, 100% { box-shadow: 0 0 5px rgba(100, 181, 246, 0.3); }
    50% { box-shadow: 0 0 20px rgba(100, 181, 246, 0.6); }
}

@keyframes learningStageShine {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

/* Learning-specific transitions */
.skill-pill {
    transition: all 0.3s ease;
}

.skill-pill:hover {
    animation: skillPillGlow 1s ease-in-out;
}

.learning-stage-badge {
    transition: all 0.3s ease;
    background-size: 200% 100%;
}

.learning-metric-card {
    transition: all 0.4s ease;
    position: relative;
    overflow: hidden;
}

.learning-metric-card:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.portfolio-ready-indicator {
    transition: all 0.3s ease;
}

.mastery-level {
    transition: all 0.3s ease;
}

.timeline-event {
    transition: all 0.6s ease;
}

.timeline-icon {
    transition: all 0.3s ease;
}

.assessment-criteria .criteria-item {
    transition: all 0.3s ease;
}

.progress-fill {
    transition: width 2s ease-out;
}

.usage-fill {
    transition: width 1.5s ease-out;
}

/* Smooth transitions for all learning containers */
.unified-dashboard-container {
    transition: all 0.4s ease;
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
    // Inject enhanced CSS animations
    document.head.insertAdjacentHTML('beforeend', enhancedDashboardAnimations);
    
    // Initialize enhanced unified dashboard manager
    window.unifiedDashboardManager = new UnifiedDashboardManager();
    
    console.log('🎓 AURA Learning-Enhanced Dashboard fully loaded and animated!');
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UnifiedDashboardManager;
}