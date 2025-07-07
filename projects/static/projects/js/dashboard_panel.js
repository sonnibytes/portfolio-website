// AURA Portfolio - Enhanced Dashboard JavaScript for Learning Focus
// Compatible with unified containers + learning-specific animations
// File: static/projects/js/dashboard_panel.js
// VERSION: Fixed for e.target.matches errors and progress bar issues

class UnifiedDashboardManager {
    constructor() {
        this.containers = new Map();
        this.animationObserver = null;
        this.learningAnimations = new Map(); // Learning-specific animations
        this.progressBarsInitialized = false; // Track progress bar state
        this.init();
    }

    init() {
        this.initializeContainers();
        this.initializeProgressBars(); // Initialize progress bars FIRST
        this.setupAnimationObserver();
        this.setupEventListeners(); // Fixed event listeners
        this.initializeLearningAnimations();
        this.startAnimations();
        console.log('🚀 Unified Dashboard Manager initialized with learning support');
    }

    // ========== FIXED PROGRESS BAR INITIALIZATION ==========
    initializeProgressBars() {
        if (this.progressBarsInitialized) return;
        
        console.log('🎯 Initializing progress bars...');
        
        // Find all progress bars and properly initialize them
        const progressBars = document.querySelectorAll('.system-progress-fill, .progress-fill');
        
        progressBars.forEach(progressBar => {
            try {
                // Get the current width from inline style or data attribute
                let percentage = 0;
                
                if (progressBar.style.width) {
                    percentage = parseFloat(progressBar.style.width.replace('%', ''));
                } else if (progressBar.dataset.targetPercentage) {
                    percentage = parseFloat(progressBar.dataset.targetPercentage);
                } else if (progressBar.dataset.progress) {
                    percentage = parseFloat(progressBar.dataset.progress);
                }
                
                // Skip if no valid percentage found
                if (isNaN(percentage) || percentage === 0) return;
                
                // Set CSS custom property for animation target
                progressBar.style.setProperty('--target-width', percentage + '%');
                
                // Remove any existing transitions
                progressBar.style.transition = 'none';
                
                // Set initial width to 0 for animation
                progressBar.style.width = '0%';
                
                // Mark as loading
                progressBar.dataset.loaded = 'false';
                
                // Use requestAnimationFrame to ensure proper timing
                requestAnimationFrame(() => {
                    // Add the animate class
                    progressBar.classList.add('animate-on-load');
                    
                    // Animate to target width
                    setTimeout(() => {
                        progressBar.style.transition = 'width 2s ease-out';
                        progressBar.style.width = percentage + '%';
                        
                        // Mark as loaded after animation
                        setTimeout(() => {
                            progressBar.dataset.loaded = 'true';
                            progressBar.classList.remove('animate-on-load');
                            progressBar.style.transition = 'none'; // Remove transition to prevent resets
                        }, 2000);
                    }, 100);
                });
                
            } catch (error) {
                console.warn('Error initializing progress bar:', error);
            }
        });
        
        this.progressBarsInitialized = true;
        console.log(`✅ Initialized ${progressBars.length} progress bars`);
    }

    // ========== FIXED METRIC COUNTER METHODS ==========
    // Replace these methods in your UnifiedDashboardManager class

    // Store original values to prevent loss during panel switching
    storeOriginalMetricValues() {
        const metrics = document.querySelectorAll('.metric-value-large, .learning-metric-value, .metric-value');
        
        metrics.forEach(metric => {
            // Only store if not already stored
            if (!metric.dataset.originalValue) {
                const text = metric.textContent.trim();
                metric.dataset.originalValue = text;
                
                // Extract numeric value for animation
                const numericValue = parseInt(text.replace(/[,\s%]/g, '')) || 0;
                metric.dataset.numericValue = numericValue;
                
                console.log(`📊 Stored metric value: "${text}" (${numericValue})`);
            }
        });
    }

    // Fixed metric counter animation that respects panel switching
    animateMetricCounters() {
        // First, store original values
        this.storeOriginalMetricValues();
        
        const metrics = document.querySelectorAll('.metric-value-large, .learning-metric-value, .metric-value');
        
        metrics.forEach(metric => {
            // Skip if already animated or currently animating
            if (metric.dataset.animated === 'true' || metric.dataset.animating === 'true') {
                return;
            }
            
            // Skip if metric is in a hidden panel
            const panel = metric.closest('[id*="panel-"], .panel-content-container > div');
            if (panel && panel.style.display === 'none') {
                return;
            }
            
            try {
                const originalValue = metric.dataset.originalValue || metric.textContent.trim();
                const finalValue = parseInt(metric.dataset.numericValue) || parseInt(originalValue.replace(/[,\s%]/g, '')) || 0;
                
                // Skip animation if value is 0 or 1 (likely already processed)
                if (finalValue <= 1) {
                    metric.textContent = originalValue;
                    metric.dataset.animated = 'true';
                    return;
                }
                
                // Mark as animating to prevent interference
                metric.dataset.animating = 'true';
                
                const duration = 1500; // 1.5 seconds
                const startTime = performance.now();
                const isPercentage = originalValue.includes('%');
                
                const animate = (currentTime) => {
                    // Check if metric is still visible (panel hasn't switched)
                    const currentPanel = metric.closest('[id*="panel-"], .panel-content-container > div');
                    if (currentPanel && currentPanel.style.display === 'none') {
                        // Panel switched - restore original value and stop
                        metric.textContent = originalValue;
                        metric.dataset.animating = 'false';
                        return;
                    }
                    
                    const elapsed = currentTime - startTime;
                    const progress = Math.min(elapsed / duration, 1);
                    
                    // Use easing function for smooth animation
                    const eased = 1 - Math.pow(1 - progress, 3);
                    const current = Math.floor(eased * finalValue);
                    
                    // Update display with proper formatting
                    if (isPercentage) {
                        metric.textContent = current + '%';
                    } else {
                        metric.textContent = current.toLocaleString();
                    }
                    
                    if (progress < 1) {
                        requestAnimationFrame(animate);
                    } else {
                        // Animation complete - set final value and mark as done
                        metric.textContent = originalValue;
                        metric.dataset.animated = 'true';
                        metric.dataset.animating = 'false';
                    }
                };
                
                // Start animation
                requestAnimationFrame(animate);
                
            } catch (error) {
                console.warn('Error animating metric counter:', error);
                // Restore original value on error
                metric.textContent = metric.dataset.originalValue || metric.textContent;
                metric.dataset.animated = 'true';
                metric.dataset.animating = 'false';
            }
        });
    }

    // Method to restore metric values when panels switch
    restoreMetricValues() {
        const metrics = document.querySelectorAll('.metric-value-large, .learning-metric-value, .metric-value');
        
        metrics.forEach(metric => {
            if (metric.dataset.originalValue) {
                // Stop any ongoing animation
                metric.dataset.animating = 'false';
                
                // Restore original value
                metric.textContent = metric.dataset.originalValue;
                
                console.log(`🔄 Restored metric value: ${metric.dataset.originalValue}`);
            }
        });
    }

    // Enhanced panel switching handler
    handlePanelSwitch() {
        console.log('🔄 Panel switch detected - restoring metric values');
        
        // Restore all metric values immediately
        this.restoreMetricValues();
        
        // Wait a moment for the panel to fully show, then animate only visible metrics
        setTimeout(() => {
            // Reset animation flags for visible metrics
            const visibleMetrics = document.querySelectorAll('.metric-value-large, .learning-metric-value, .metric-value');
            visibleMetrics.forEach(metric => {
                const panel = metric.closest('[id*="panel-"], .panel-content-container > div');
                if (!panel || panel.style.display !== 'none') {
                    metric.dataset.animated = 'false';
                    metric.dataset.animating = 'false';
                }
            });
            
            // Animate only visible metrics
            this.animateMetricCounters();
        }, 100);
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
        if (container.querySelector('.alert-dismiss, .alert-content')) return 'alert';
        if (container.querySelector('.status-indicator, .health-status')) return 'status';
        if (container.querySelector('.dashboard-metric, .dashboard-summary')) return 'dashboard';
        return 'component'; // Default fallback
    }

    getContainerColor(container) {
        const colorClasses = ['teal', 'purple', 'coral', 'lavender', 'mint', 'yellow', 'navy', 'gunmetal'];
        for (const color of colorClasses) {
            if (container.classList.contains(color)) return color;
            }
        return 'teal'; // Default color
    }

    initializeContainerType(container, type) {
        switch (type) {
            case 'dashboard':
                this.initializeDashboardContainer(container);
                break;
            case 'metric':
                this.initializeMetricContainer(container);
                break;
            case 'chart':
                this.initializeChartContainer(container);
                break;
            case 'alert':
                this.initializeAlertContainer(container);
                break;
            case 'status':
                this.initializeStatusContainer(container);
                break;
            default:
                this.initializeGenericContainer(container);
        }
    }

    // ========== FIXED EVENT LISTENERS ==========
    setupEventListeners() {
        console.log('🎧 Setting up event listeners with safety checks...');
        
        // FIXED: Enhanced hover effects with safety checks
        document.addEventListener('mouseenter', (e) => {
            // Safety check: ensure target is an Element and has matches method
            if (e.target && typeof e.target.matches === 'function') {
                if (e.target.matches('.skill-pill, .learning-stage-badge, .mastery-level')) {
                e.target.style.transition = 'all 0.2s ease';
            }
            }
        }, true);
    
        // FIXED: Learning card interactions with safety checks
        document.addEventListener('click', (e) => {
            // Safety check: ensure target is an Element and has matches method
            if (e.target && typeof e.target.matches === 'function') {
                if (e.target.matches('.learning-metric-card, .skill-progression-item')) {
                // Add click ripple effect
                this.addRippleEffect(e.target, e);
            }
            }
        });
    
        // FIXED: Enhanced panel interactions with safety checks
        document.addEventListener('mouseover', (e) => {
            // Safety check for all hover interactions
            if (e.target && typeof e.target.matches === 'function') {
                // Dashboard container hover effects
                if (e.target.matches('.unified-dashboard-container')) {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.3)';
                }
                
                // Metric card hover effects
                if (e.target.matches('.learning-metric-card')) {
                    e.target.style.background = 'rgba(255, 255, 255, 0.08)';
                    e.target.style.borderColor = 'rgba(255, 255, 255, 0.3)';
                }
            }
        });
    
        document.addEventListener('mouseout', (e) => {
            // Safety check for all hover out interactions
            if (e.target && typeof e.target.matches === 'function') {
                // Reset dashboard container styles
                if (e.target.matches('.unified-dashboard-container')) {
                    e.target.style.transform = '';
                    e.target.style.boxShadow = '';
                }
                
                // Reset metric card styles
                if (e.target.matches('.learning-metric-card')) {
                    e.target.style.background = '';
                    e.target.style.borderColor = '';
                }
            }
        });
    
        // FIXED: Button and link interactions with safety checks
        document.addEventListener('click', (e) => {
            // Safety check for button interactions
            if (e.target && typeof e.target.matches === 'function') {
                // Handle alert dismissals
                if (e.target.matches('.alert-dismiss')) {
                    const alert = e.target.closest('.unified-dashboard-container');
                    if (alert) {
                        alert.style.transform = 'translateX(100%)';
                        alert.style.opacity = '0';
                        setTimeout(() => alert.remove(), 300);
                    }
                }
                
                // Handle chart toggles
                if (e.target.matches('.chart-toggle')) {
                    const chart = e.target.closest('.unified-dashboard-container').querySelector('.chart-placeholder');
                    if (chart) {
                        chart.style.display = chart.style.display === 'none' ? 'block' : 'none';
                    }
                }
            }
        });

        console.log('✅ Event listeners setup complete with safety checks');
    }

    // ========== LEARNING-SPECIFIC ANIMATIONS ==========
    initializeLearningAnimations() {
        // Enhanced learning-specific animations
        this.setupSkillPillAnimations();
        this.setupLearningMetricAnimations();
        this.setupLearningStageAnimations();
        console.log('🎓 Learning animations initialized');
    }

    setupSkillPillAnimations() {
        const skillPills = document.querySelectorAll('.skill-pill');
        skillPills.forEach((pill, index) => {
            pill.style.animationDelay = `${index * 0.1}s`;
            pill.classList.add('animate-on-scroll');
        });
    }

    setupLearningMetricAnimations() {
        const metricCards = document.querySelectorAll('.learning-metric-card');
        metricCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-4px) scale(1.02)';
                card.style.boxShadow = '0 12px 40px rgba(0, 0, 0, 0.15)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = '';
                card.style.boxShadow = '';
            });
        });
    }

    setupLearningStageAnimations() {
        const stageBadges = document.querySelectorAll('.learning-stage-badge');
        stageBadges.forEach(badge => {
            badge.addEventListener('mouseenter', () => {
                badge.style.animation = 'learningStageShine 1s ease-in-out';
            });
        });
    }

    // ========== ANIMATION OBSERVER ==========
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

    // ========== RIPPLE EFFECT ==========
    addRippleEffect(element, event) {
        try {
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
        } catch (error) {
            console.warn('Error creating ripple effect:', error);
        }
    }

    // ========== START ANIMATIONS ==========
    startAnimations() {
        // Delay metric counter animations to avoid conflicts with progress bars
        setTimeout(() => {
            this.animateMetricCounters();
        }, 300);
        
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

    // ========== CONTAINER TYPE INITIALIZERS ==========
    
    initializeDashboardContainer(container) {
        container.style.opacity = '0';
        container.style.transform = 'translateY(20px)';
        setTimeout(() => {
            container.style.opacity = '1';
            container.style.transform = 'translateY(0)';
            container.style.transition = 'all 0.6s ease';
        }, 100);
    }

    initializeMetricContainer(container) {
        // Enhanced metric container with counter animation delay
        const metricValues = container.querySelectorAll('.metric-value-large, .metric-value');
        metricValues.forEach(value => {
            value.style.opacity = '0';
            setTimeout(() => {
                value.style.opacity = '1';
                value.style.transition = 'opacity 0.5s ease';
            }, 200);
        });
    }

    initializeChartContainer(container) {
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
        const statusIndicators = container.querySelectorAll('.status-indicator');
        statusIndicators.forEach(indicator => {
            const status = indicator.dataset.status;
            if (status === 'active' || status === 'portfolio-ready') {
                indicator.style.animation = 'pulse 2s ease-in-out infinite';
            }
        });
    }

    initializeGenericContainer(container) {
        // Default container initialization
        container.style.transition = 'all 0.4s ease';
    }

    // ========== ENHANCED METHOD FOR LEARNING SYSTEM DASHBOARD ==========
    // Updated initialization method
    initializeLearningSystemDashboard() {
        console.log('🎛️ Initializing Learning System Dashboard');
        
        // Store original values first
        this.storeOriginalMetricValues();
        
        // Initialize progress bars FIRST (before other animations)
        this.initializeProgressBars();
        
        // Set up panel switching detection
        this.setupPanelSwitchDetection();
        
        // Wait a bit before starting other animations to prevent conflicts
        setTimeout(() => {
            // Initialize metric counters
            this.animateMetricCounters();
            
            // Initialize other dashboard components
            this.setupEventListeners();
            this.setupAnimationObserver();
            
            // Start general animations
            this.startAnimations();
        }, 200);
    }

    // New method to detect panel switching
    setupPanelSwitchDetection() {
        // Listen for panel link clicks
        const panelLinks = document.querySelectorAll('.control-panel-link');
        panelLinks.forEach(link => {
            link.addEventListener('click', () => {
                console.log('🎯 Panel link clicked - preparing for switch');
                // Small delay to let the panel switch happen
                setTimeout(() => {
                    this.handlePanelSwitch();
                }, 50);
            });
        });
        
        // Also listen for any dynamic content changes
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    // Panel visibility might have changed
                    const target = mutation.target;
                    if (target.classList.contains('panel-content-container') || 
                        target.closest('.panel-content-container')) {
                        this.handlePanelSwitch();
                    }
                }
            });
        });
        
        // Observe the main panel container
        const panelContainer = document.querySelector('.panel-content-container');
        if (panelContainer) {
            observer.observe(panelContainer, {
                attributes: true,
                subtree: true,
                attributeFilter: ['style', 'class']
            });
        }
        
        console.log('👁️ Panel switch detection setup complete');
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

/* FIXED: Stable progress bar styles */
.progress-fill {
    transition: none; /* Remove automatic transitions */
}

.progress-fill.animate-on-load {
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
    console.log('🚀 Dashboard Panel JS: DOM Content Loaded');
    
    // Inject enhanced CSS animations
    document.head.insertAdjacentHTML('beforeend', enhancedDashboardAnimations);
    
    // Initialize enhanced unified dashboard manager
    try {
    window.unifiedDashboardManager = new UnifiedDashboardManager();
    console.log('🎓 AURA Learning-Enhanced Dashboard fully loaded and animated!');
    } catch (error) {
        console.error('❌ Error initializing dashboard manager:', error);
        
        // Fallback: Initialize progress bars directly
        console.log('🔧 Falling back to direct progress bar initialization');
        
        const progressBars = document.querySelectorAll('.system-progress-fill, .progress-fill');
        progressBars.forEach(progressBar => {
            try {
                const percentage = progressBar.style.width || '0%';
                if (percentage !== '0%') {
                    progressBar.style.transition = 'none';
                    progressBar.style.width = '0%';
                    
                    setTimeout(() => {
                        progressBar.style.transition = 'width 2s ease-out';
                        progressBar.style.width = percentage;
                    }, 100);
                }
            } catch (error) {
                console.warn('Error in fallback progress bar init:', error);
            }
        });
    }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UnifiedDashboardManager;
}