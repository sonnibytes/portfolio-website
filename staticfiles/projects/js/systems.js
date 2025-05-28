/**
 * AURA Systems Interface - JavaScript
 * Advanced User Repository & Archive - Systems Command Center
 * Version: 1.0.0
 */

// Systems Interface State
const SystemsInterface = {
    initialized: false,
    filterPanelOpen: false,
    dataOverlayActive: false,
    currentFilters: {},
    realTimeData: null,
    updateInterval: null
};

/**
 * Initialize Systems Interface
 */
function initSystemsInterface() {
    console.log('🚀 AURA Systems Interface Initializing...');
    
    if (SystemsInterface.initialized) return;
    
    // Initialize core components
    initFilterPanel();
    initDataOverlay();
    initRealTimeMetrics();
    initAlertSystem();
    initSubnavScroll();
    initKeyboardShortcuts();
    
    // Mark as initialized
    SystemsInterface.initialized = true;
    console.log('✅ Systems Interface Online');
}

/**
 * Filter Panel Management
 */
function initFilterPanel() {
    const filterToggle = document.getElementById('systemsFilterToggle');
    const filterPanel = document.getElementById('systemsFilterPanel');
    const filterClose = document.getElementById('closeFilters');
    const clearFilters = document.getElementById('clearFilters');
    const filterForm = document.getElementById('systemsFilterForm');
    
    if (!filterToggle || !filterPanel) return;
    
    // Toggle filter panel
    filterToggle.addEventListener('click', function() {
        toggleFilterPanel();
    });
    
    // Close filter panel
    if (filterClose) {
        filterClose.addEventListener('click', function() {
            hideFilterPanel();
        });
    }
    
    // Clear all filters
    if (clearFilters) {
        clearFilters.addEventListener('click', function() {
            clearAllFilters();
        });
    }
    
    // Technology search
    const techSearch = document.getElementById('techSearch');
    if (techSearch) {
        techSearch.addEventListener('input', function() {
            filterTechnologies(this.value);
        });
    }
    
    // Complexity range sliders
    const complexityMin = document.getElementById('complexityMin');
    const complexityMax = document.getElementById('complexityMax');
    const complexityDisplay = document.getElementById('complexityDisplay');
    
    if (complexityMin && complexityMax && complexityDisplay) {
        function updateComplexityDisplay() {
            const min = parseInt(complexityMin.value);
            const max = parseInt(complexityMax.value);
            
            // Ensure min <= max
            if (min > max) {
                if (this === complexityMin) {
                    complexityMax.value = min;
                } else {
                    complexityMin.value = max;
                }
            }
            
            complexityDisplay.textContent = `${complexityMin.value} - ${complexityMax.value}`;
        }
        
        complexityMin.addEventListener('input', updateComplexityDisplay);
        complexityMax.addEventListener('input', updateComplexityDisplay);
        
        // Initialize display
        updateComplexityDisplay();
    }
    
    // Form submission with loading state
    if (filterForm) {
        filterForm.addEventListener('submit', function() {
            showLoadingState();
        });
    }
}

function toggleFilterPanel() {
    const filterPanel = document.getElementById('systemsFilterPanel');
    const filterToggle = document.getElementById('systemsFilterToggle');
    
    if (!filterPanel) return;
    
    if (SystemsInterface.filterPanelOpen) {
        hideFilterPanel();
    } else {
        showFilterPanel();
    }
}

function showFilterPanel() {
    const filterPanel = document.getElementById('systemsFilterPanel');
    const filterToggle = document.getElementById('systemsFilterToggle');
    
    if (!filterPanel) return;
    
    filterPanel.style.display = 'block';
    filterPanel.classList.add('systems-fade-in');
    filterToggle.classList.add('active');
    
    SystemsInterface.filterPanelOpen = true;
    
    // Smooth scroll to filters
    setTimeout(() => {
        filterPanel.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'nearest' 
        });
    }, 100);
}

function hideFilterPanel() {
    const filterPanel = document.getElementById('systemsFilterPanel');
    const filterToggle = document.getElementById('systemsFilterToggle');
    
    if (!filterPanel) return;
    
    filterPanel.style.display = 'none';
    filterPanel.classList.remove('systems-fade-in');
    filterToggle.classList.remove('active');
    
    SystemsInterface.filterPanelOpen = false;
}

function clearAllFilters() {
    const filterForm = document.getElementById('systemsFilterForm');
    if (!filterForm) return;
    
    // Clear all checkboxes
    const checkboxes = filterForm.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
    
    // Reset range sliders
    const complexityMin = document.getElementById('complexityMin');
    const complexityMax = document.getElementById('complexityMax');
    if (complexityMin && complexityMax) {
        complexityMin.value = 1;
        complexityMax.value = 5;
        document.getElementById('complexityDisplay').textContent = '1 - 5';
    }
    
    // Clear search
    const techSearch = document.getElementById('techSearch');
    if (techSearch) {
        techSearch.value = '';
        filterTechnologies('');
    }
    
    // Submit form to apply cleared filters
    setTimeout(() => {
        filterForm.submit();
    }, 100);
}

function filterTechnologies(searchTerm) {
    const techOptions = document.querySelectorAll('.tech-option');
    const term = searchTerm.toLowerCase().trim();
    
    techOptions.forEach(option => {
        const techName = option.dataset.tech || '';
        const isVisible = !term || techName.includes(term);
        
        option.classList.toggle('visible', isVisible);
        option.style.display = isVisible ? 'flex' : 'none';
    });
}

/**
 * Real-time Data Overlay
 */
function initDataOverlay() {
    const dataOverlay = document.getElementById('systemsDataOverlay');
    if (!dataOverlay) return;
    
    // Show overlay on hover over metrics
    const statItems = document.querySelectorAll('.stat-item');
    statItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            showDataOverlay();
        });
    });
    
    // Hide overlay when mouse leaves both stats and overlay
    let hideTimeout;
    
    function scheduleHide() {
        hideTimeout = setTimeout(hideDataOverlay, 500);
    }
    
    function cancelHide() {
        if (hideTimeout) {
            clearTimeout(hideTimeout);
            hideTimeout = null;
        }
    }
    
    statItems.forEach(item => {
        item.addEventListener('mouseleave', scheduleHide);
    });
    
    dataOverlay.addEventListener('mouseenter', cancelHide);
    dataOverlay.addEventListener('mouseleave', scheduleHide);
}

function showDataOverlay() {
    const dataOverlay = document.getElementById('systemsDataOverlay');
    if (!dataOverlay) return;
    
    dataOverlay.classList.add('active');
    SystemsInterface.dataOverlayActive = true;
    
    // Populate with real-time data
    updateDataStream();
}

function hideDataOverlay() {
    const dataOverlay = document.getElementById('systemsDataOverlay');
    if (!dataOverlay) return;
    
    dataOverlay.classList.remove('active');
    SystemsInterface.dataOverlayActive = false;
}

function updateDataStream() {
    const dataStream = document.getElementById('dataStream');
    if (!dataStream) return;
    
    const timestamp = new Date().toISOString().slice(0, 19).replace('T', ' ');
    const metrics = [
        `[${timestamp}] CPU: ${Math.floor(Math.random() * 30 + 15)}%`,
        `[${timestamp}] MEM: ${Math.floor(Math.random() * 20 + 60)}%`,
        `[${timestamp}] NET: ${Math.floor(Math.random() * 100 + 50)}KB/s`,
        `[${timestamp}] SYS: ${Math.floor(Math.random() * 50 + 150)}ms`,
        `[${timestamp}] UPT: 99.${Math.floor(Math.random() * 9 + 1)}%`
    ];
    
    dataStream.innerHTML = metrics.map(metric => 
        `<div class="data-line">${metric}</div>`
    ).join('');
}

/**
 * Real-time Metrics Updates
 */
function initRealTimeMetrics() {
    // Update stats every 5 seconds
    SystemsInterface.updateInterval = setInterval(() => {
        updateSystemStats();
        if (SystemsInterface.dataOverlayActive) {
            updateDataStream();
        }
    }, 5000);
}

function updateSystemStats() {
    const statValues = document.querySelectorAll('.stat-value');
    
    statValues.forEach(stat => {
        const currentValue = parseInt(stat.textContent);
        if (!isNaN(currentValue)) {
            // Small random fluctuation
            const variation = Math.floor(Math.random() * 3) - 1; // -1, 0, or 1
            const newValue = Math.max(0, currentValue + variation);
            
            if (stat.textContent.includes('%')) {
                stat.textContent = Math.min(100, newValue) + '%';
            } else {
                stat.textContent = newValue.toString();
            }
            
            // Add glow effect on change
            if (variation !== 0) {
                stat.style.textShadow = '0 0 12px rgba(38, 198, 218, 0.6)';
                setTimeout(() => {
                    stat.style.textShadow = '0 0 8px rgba(38, 198, 218, 0.3)';
                }, 300);
            }
        }
    });
}

/**
 * Alert System
 */
function initAlertSystem() {
    const alertDismissButtons = document.querySelectorAll('.alert-dismiss');
    
    alertDismissButtons.forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.closest('.alert');
            if (alert) {
                dismissAlert(alert);
            }
        });
    });
    
    // Auto-dismiss alerts after 10 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                dismissAlert(alert);
            }
        }, 10000);
    });
}

function dismissAlert(alertElement) {
    alertElement.style.opacity = '0';
    alertElement.style.transform = 'translateX(100%)';
    
    setTimeout(() => {
        if (alertElement.parentNode) {
            alertElement.remove();
        }
    }, 300);
}

/**
 * Subnav Scroll Effects
 */
function initSubnavScroll() {
    const subnav = document.querySelector('.systems-subnav');
    if (!subnav) return;
    
    let lastScrollY = window.scrollY;
    
    window.addEventListener('scroll', throttle(() => {
        const currentScrollY = window.scrollY;
        
        // Add/remove scrolled class for styling
        if (currentScrollY > 100) {
            subnav.classList.add('scrolled');
        } else {
            subnav.classList.remove('scrolled');
        }
        
        lastScrollY = currentScrollY;
    }, 16)); // ~60fps
}

/**
 * Keyboard Shortcuts
 */
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(event) {
        // Only trigger if not in an input field
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }
        
        switch (event.key) {
            case 'f':
            case 'F':
                if (event.ctrlKey || event.metaKey) {
                    event.preventDefault();
                    toggleFilterPanel();
                }
                break;
                
            case 'Escape':
                if (SystemsInterface.filterPanelOpen) {
                    hideFilterPanel();
                }
                if (SystemsInterface.dataOverlayActive) {
                    hideDataOverlay();
                }
                break;
                
            case 'r':
            case 'R':
                if (event.ctrlKey || event.metaKey) {
                    event.preventDefault();
                    refreshSystemsData();
                }
                break;
        }
    });
}

/**
 * Loading States
 */
function showLoadingState() {
    const container = document.querySelector('.systems-main-content');
    if (container) {
        container.classList.add('loading');
    }
    
    // Show loading in subnav
    const filterToggle = document.getElementById('systemsFilterToggle');
    if (filterToggle) {
        filterToggle.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Loading...</span>';
    }
}

function hideLoadingState() {
    const container = document.querySelector('.systems-main-content');
    if (container) {
        container.classList.remove('loading');
    }
    
    // Restore filter toggle
    const filterToggle = document.getElementById('systemsFilterToggle');
    if (filterToggle) {
        filterToggle.innerHTML = '<i class="fas fa-filter"></i><span>Filters</span>';
    }
}

/**
 * Data Refresh
 */
function refreshSystemsData() {
    showLoadingState();
    
    // Simulate data refresh
    setTimeout(() => {
        updateSystemStats();
        hideLoadingState();
        
        // Show success notification
        showNotification('Systems data refreshed', 'success');
    }, 1000);
}

/**
 * Notification System
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `systems-notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Style the notification
    Object.assign(notification.style, {
        position: 'fixed',
        top: '100px',
        right: '20px',
        background: 'var(--gradient-glass), rgba(13, 13, 31, 0.9)',
        border: '1px solid rgba(38, 198, 218, 0.3)',
        borderRadius: 'var(--border-radius-lg)',
        padding: 'var(--spacing-md)',
        color: 'var(--color-text)',
        zIndex: 'var(--z-notification)',
        backdropFilter: 'blur(20px)',
        transform: 'translateX(100%)',
        transition: 'transform 0.3s ease',
        minWidth: '300px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'
    });
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 50);
    
    // Add close functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        dismissNotification(notification);
    });
    
    // Auto-dismiss after 4 seconds
    setTimeout(() => {
        dismissNotification(notification);
    }, 4000);
}

function dismissNotification(notification) {
    notification.style.transform = 'translateX(100%)';
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 300);
}

function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Systems Grid Animation
 */
function animateSystemsGrid() {
    const gridItems = document.querySelectorAll('.grid-item, .system-card, .metric-card');
    
    gridItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

/**
 * System Card Interactions
 */
function initSystemCardInteractions() {
    const systemCards = document.querySelectorAll('.system-card, .grid-item');
    
    systemCards.forEach(card => {
        // Add hover scanning effect
        card.addEventListener('mouseenter', function() {
            const scanLine = this.querySelector('.item-scanning-line, .card-scanning-line');
            if (scanLine) {
                scanLine.style.animation = 'scanHorizontal 1s linear';
            }
        });
        
        // Reset animation
        card.addEventListener('mouseleave', function() {
            const scanLine = this.querySelector('.item-scanning-line, .card-scanning-line');
            if (scanLine) {
                setTimeout(() => {
                    scanLine.style.animation = '';
                }, 1000);
            }
        });
        
        // Add click ripple effect
        card.addEventListener('click', function(e) {
            if (e.target.tagName === 'A' || e.target.closest('a')) return;
            
            const ripple = document.createElement('div');
            ripple.style.cssText = `
                position: absolute;
                border-radius: 50%;
                background: rgba(38, 198, 218, 0.3);
                transform: scale(0);
                animation: ripple 0.6s linear;
                pointer-events: none;
            `;
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
            ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
            
            this.style.position = 'relative';
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

/**
 * Progress Bar Animations
 */
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar, .progress-bar-hud');
    
    progressBars.forEach(bar => {
        const targetWidth = bar.style.width || bar.dataset.width || '0%';
        bar.style.width = '0%';
        
        // Animate to target width
        setTimeout(() => {
            bar.style.transition = 'width 1s ease-out';
            bar.style.width = targetWidth;
        }, 500);
    });
}

/**
 * System Status Updates
 */
function updateSystemStatus(systemId, status, message) {
    const statusIndicators = document.querySelectorAll(`[data-system="${systemId}"] .status-indicator`);
    const statusTexts = document.querySelectorAll(`[data-system="${systemId}"] .status-text`);
    
    statusIndicators.forEach(indicator => {
        indicator.className = `status-indicator ${status}`;
    });
    
    statusTexts.forEach(text => {
        text.textContent = message.toUpperCase();
    });
    
    // Show notification
    showNotification(`System ${systemId}: ${message}`, getStatusType(status));
}

function getStatusType(status) {
    const statusTypes = {
        'operational': 'success',
        'deployed': 'success',
        'warning': 'warning',
        'in_development': 'info',
        'testing': 'warning',
        'error': 'error',
        'archived': 'info'
    };
    return statusTypes[status] || 'info';
}

/**
 * Advanced Filtering
 */
function applyAdvancedFilters(filters) {
    const items = document.querySelectorAll('.grid-item, .system-card');
    let visibleCount = 0;
    
    items.forEach(item => {
        let shouldShow = true;
        
        // Check status filter
        if (filters.status && filters.status.length > 0) {
            const itemStatus = item.dataset.status;
            shouldShow = shouldShow && filters.status.includes(itemStatus);
        }
        
        // Check type filter
        if (filters.type && filters.type.length > 0) {
            const itemType = item.dataset.type;
            shouldShow = shouldShow && filters.type.includes(itemType);
        }
        
        // Check technology filter
        if (filters.tech && filters.tech.length > 0) {
            const itemTech = (item.dataset.technologies || '').split(',');
            shouldShow = shouldShow && filters.tech.some(tech => itemTech.includes(tech));
        }
        
        // Check complexity filter
        if (filters.complexityMin || filters.complexityMax) {
            const itemComplexity = parseInt(item.dataset.complexity);
            const min = parseInt(filters.complexityMin) || 1;
            const max = parseInt(filters.complexityMax) || 5;
            shouldShow = shouldShow && (itemComplexity >= min && itemComplexity <= max);
        }
        
        // Apply visibility
        if (shouldShow) {
            item.style.display = '';
            item.classList.add('systems-fade-in');
            visibleCount++;
        } else {
            item.style.display = 'none';
            item.classList.remove('systems-fade-in');
        }
    });
    
    // Update results count
    updateResultsCount(visibleCount);
}

function updateResultsCount(count) {
    const countElements = document.querySelectorAll('.count-value, .results-count .count-value');
    countElements.forEach(element => {
        element.textContent = formatNumber(count);
    });
}

/**
 * Search Functionality
 */
function initSystemsSearch() {
    const searchInput = document.getElementById('systemsSearch');
    if (!searchInput) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim().toLowerCase();
        
        searchTimeout = setTimeout(() => {
            performSearch(query);
        }, 300);
    });
}

function performSearch(query) {
    const items = document.querySelectorAll('.grid-item, .system-card');
    let visibleCount = 0;
    
    items.forEach(item => {
        const title = (item.querySelector('.item-title, .card-title')?.textContent || '').toLowerCase();
        const description = (item.querySelector('.item-excerpt, .card-description')?.textContent || '').toLowerCase();
        const tags = (item.dataset.tags || '').toLowerCase();
        
        const matches = !query || 
            title.includes(query) || 
            description.includes(query) || 
            tags.includes(query);
        
        if (matches) {
            item.style.display = '';
            item.classList.add('systems-fade-in');
            visibleCount++;
        } else {
            item.style.display = 'none';
            item.classList.remove('systems-fade-in');
        }
    });
    
    updateResultsCount(visibleCount);
}

/**
 * Export and Utility Functions
 */

// Utility function for throttling
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Utility function for debouncing
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = function() {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

// Format numbers with K/M suffixes
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// Generate system scanning effects
function addScanningEffect(element) {
    if (!element) return;
    
    const scanLine = document.createElement('div');
    scanLine.className = 'scanning-line';
    scanLine.style.cssText = `
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent 0%, rgba(38, 198, 218, 0.3) 50%, transparent 100%);
        animation: scanHorizontal 2s linear infinite;
        pointer-events: none;
        z-index: 1;
    `;
    
    element.style.position = 'relative';
    element.appendChild(scanLine);
    
    return scanLine;
}

// Export functions for global access
window.SystemsInterface = SystemsInterface;
window.initSystemsInterface = initSystemsInterface;
window.showFilterPanel = showFilterPanel;
window.hideFilterPanel = hideFilterPanel;
window.updateSystemStatus = updateSystemStatus;
window.showNotification = showNotification;
window.animateSystemsGrid = animateSystemsGrid;
window.refreshSystemsData = refreshSystemsData;

// CSS for ripple effect
const rippleCSS = `
@keyframes ripple {
    to {
        transform: scale(4);
        opacity: 0;
    }
}
`;

// Add ripple CSS to document
if (!document.getElementById('systems-ripple-css')) {
    const style = document.createElement('style');
    style.id = 'systems-ripple-css';
    style.textContent = rippleCSS;
    document.head.appendChild(style);
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Delay initialization slightly to ensure all components are ready
        setTimeout(initSystemsInterface, 100);
    });
} else {
    setTimeout(initSystemsInterface, 100);
}

// Initialize additional components when interface is ready
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        initSystemCardInteractions();
        animateProgressBars();
        animateSystemsGrid();
        initSystemsSearch();
    }, 200);
});