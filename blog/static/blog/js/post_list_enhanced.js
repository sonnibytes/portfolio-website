/**
 * Enhanced DataLogs Post List JavaScript - CLEANED
 * Advanced functionality for the DataLogs interface
 * Version: 2.1.0 - Cleaned and Optimized
 */

// DataLogs Interface State
const DataLogsEnhanced = {
    initialized: false,
    currentView: 'grid',
    searchTimeout: null,
    categoryScrollPosition: 0
};

/**
 * Initialize Enhanced DataLogs Interface
 */
function initEnhancedDataLogs() {
    console.log('🚀 Enhanced DataLogs Interface Initializing...');
    
    // Initialize all enhanced features
    initCategoryNavigation();
    initEnhancedSearch();
    initViewToggleSystem();
    initCardAnimations();
    initTerminalEnhancements();
    initScrollEffects();
    initCategoryColorSystem();
    
    // Mark as initialized
    DataLogsEnhanced.initialized = true;
    console.log('✅ Enhanced DataLogs Interface Online');
}

/**
 * Initialize Category Navigation with Glass Hexagons
 */
function initCategoryNavigation() {
    const scrollContainer = document.getElementById('categoriesGrid');
    const leftBtn = document.getElementById('categoryScrollLeft');
    const rightBtn = document.getElementById('categoryScrollRight');
    
    if (!scrollContainer || !leftBtn || !rightBtn) {
        console.log('📂 Category navigation elements not found, skipping...');
        return;
    }
    
    console.log('📂 Initializing category navigation...');
    
    // Enhanced scroll button logic
    function updateScrollButtons() {
        const { scrollLeft, scrollWidth, clientWidth } = scrollContainer;
        const maxScroll = scrollWidth - clientWidth;
        
        // Left button state
        leftBtn.style.opacity = scrollLeft > 10 ? '1' : '0.3';
        leftBtn.disabled = scrollLeft <= 10;
        leftBtn.style.transform = scrollLeft > 10 ? 'scale(1)' : 'scale(0.9)';
        
        // Right button state
        rightBtn.style.opacity = scrollLeft < maxScroll - 10 ? '1' : '0.3';
        rightBtn.disabled = scrollLeft >= maxScroll - 10;
        rightBtn.style.transform = scrollLeft < maxScroll - 10 ? 'scale(1)' : 'scale(0.9)';
        
        // Store current position
        DataLogsEnhanced.categoryScrollPosition = scrollLeft;
    }
    
    // Smooth scrolling with momentum
    function smoothScroll(direction) {
        const scrollAmount = 300;
        const targetScroll = direction === 'left' 
            ? Math.max(0, scrollContainer.scrollLeft - scrollAmount)
            : Math.min(scrollContainer.scrollWidth - scrollContainer.clientWidth, 
                      scrollContainer.scrollLeft + scrollAmount);
        
        scrollContainer.scrollTo({
            left: targetScroll,
            behavior: 'smooth'
        });
        
        // Add visual feedback
        const btn = direction === 'left' ? leftBtn : rightBtn;
        animateButtonPress(btn);
    }
    
    // Button press animation
    function animateButtonPress(button) {
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            button.style.transform = button.disabled ? 'scale(0.9)' : 'scale(1)';
        }, 150);
    }
    
    // Event listeners
    leftBtn.addEventListener('click', () => smoothScroll('left'));
    rightBtn.addEventListener('click', () => smoothScroll('right'));
    
    // Update buttons on scroll with throttling
    let scrollTimeout;
    scrollContainer.addEventListener('scroll', () => {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(updateScrollButtons, 50);
    });
    
    // Initial button state
    setTimeout(updateScrollButtons, 100);
    
    // Update on window resize
    window.addEventListener('resize', throttle(updateScrollButtons, 150));
    
    // Enhanced category card interactions
    const categoryCards = document.querySelectorAll('.category-nav-item');
    categoryCards.forEach((card, index) => {
        // Click animation with ripple effect
        card.addEventListener('click', function(e) {
            // Add loading state
            this.classList.add('category-loading');
            
            // Create ripple effect
            createRippleEffect(this, e);
            
            // Animate hexagon
            const hexagon = this.querySelector('.category-hexagon.glass-hex');
            if (hexagon) {
                hexagon.style.transform = 'scale(0.9)';
                setTimeout(() => {
                    hexagon.style.transform = 'scale(1)';
                }, 200);
            }
        });
        
        // Entrance animation with stagger
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100);
    });
    
    // Touch/swipe support for mobile
    let touchStartX = 0;
    let touchStartScrollLeft = 0;
    let isDragging = false;
    
    scrollContainer.addEventListener('touchstart', function(e) {
        touchStartX = e.touches[0].pageX;
        touchStartScrollLeft = scrollContainer.scrollLeft;
        isDragging = true;
    }, { passive: true });
    
    scrollContainer.addEventListener('touchmove', function(e) {
        if (!isDragging) return;
        
        const x = e.touches[0].pageX;
        const walk = (touchStartX - x) * 2;
        scrollContainer.scrollLeft = touchStartScrollLeft + walk;
    }, { passive: true });
    
    scrollContainer.addEventListener('touchend', function() {
        isDragging = false;
    });
    
    console.log('✅ Category navigation initialized');
}

/**
 * Initialize Category Color System
 */
function initCategoryColorSystem() {
    const categoryItems = document.querySelectorAll('.category-nav-item');
    const categoryBadges = document.querySelectorAll('.category-badge[data-color]');
    
    // Apply colors to category hexagons
    categoryItems.forEach(item => {
        const hexagon = item.querySelector('.category-hexagon.glass-hex');
        if (hexagon && hexagon.dataset.color) {
            const color = hexagon.dataset.color;
            hexagon.style.setProperty('--hex-color', color);
        }
    });
    
    // Apply colors to category badges
    categoryBadges.forEach(badge => {
        if (badge.dataset.color) {
            const color = badge.dataset.color;
            badge.style.setProperty('--category-color', color);
        }
    });
}

/**
 * Enhanced Search with Real-time Suggestions
 */
function initEnhancedSearch() {
    const searchInput = document.querySelector('.search-input-enhanced');
    const suggestions = document.getElementById('searchSuggestions');
    const quickFilters = document.querySelectorAll('.filter-tag');
    
    if (!searchInput) return;
    
    console.log('🔍 Initializing enhanced search...');
    
    // Real-time search suggestions
    searchInput.addEventListener('input', function() {
        clearTimeout(DataLogsEnhanced.searchTimeout);
        const query = this.value.trim();
        
        if (query.length >= 2) {
            // Add loading indicator
            this.classList.add('search-loading');
            
            DataLogsEnhanced.searchTimeout = setTimeout(() => {
                loadSearchSuggestions(query);
                this.classList.remove('search-loading');
            }, 300);
        } else {
            hideSuggestions();
        }
    });
    
    // Enhanced suggestion loading
    function loadSearchSuggestions(query) {
        if (!suggestions) return;
        
        // Mock suggestions with categories (replace with actual API call)
        const mockSuggestions = [
            { text: 'Machine Learning Fundamentals', category: 'ML', icon: 'fas fa-brain' },
            { text: 'Python Data Analysis', category: 'DEV', icon: 'fab fa-python' },
            { text: 'Django Best Practices', category: 'DEV', icon: 'fas fa-code' },
            { text: 'API Development Guide', category: 'DEV', icon: 'fas fa-plug' },
            { text: 'Database Optimization', category: 'DATA', icon: 'fas fa-database' },
            { text: 'Neural Network Implementation', category: 'ML', icon: 'fas fa-project-diagram' }
        ].filter(suggestion => 
            suggestion.text.toLowerCase().includes(query.toLowerCase())
        ).slice(0, 5);
        
        if (mockSuggestions.length > 0) {
            suggestions.innerHTML = mockSuggestions.map(suggestion => 
                `<div class="search-suggestion" onclick="selectSuggestion('${suggestion.text}')">
                    <i class="${suggestion.icon}"></i>
                    <div class="suggestion-content">
                        <span class="suggestion-text">${highlightQuery(suggestion.text, query)}</span>
                        <span class="suggestion-category">${suggestion.category}</span>
                    </div>
                </div>`
            ).join('');
            
            showSuggestions();
        } else {
            hideSuggestions();
        }
    }
    
    function highlightQuery(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
    
    function showSuggestions() {
        if (suggestions) {
            suggestions.classList.add('show');
        }
    }
    
    function hideSuggestions() {
        if (suggestions) {
            suggestions.classList.remove('show');
        }
    }
    
    // Global function for suggestion selection
    window.selectSuggestion = function(suggestion) {
        searchInput.value = suggestion;
        hideSuggestions();
        searchInput.closest('form').submit();
    };
    
    // Enhanced quick filters
    quickFilters.forEach(filter => {
        filter.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Toggle active state
            this.classList.toggle('active');
            
            // Add click animation
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
            
            // Show feedback
            setTimeout(() => {
                showNotification(`Filter "${this.textContent.trim()}" ${this.classList.contains('active') ? 'applied' : 'removed'}`, 'info');
            }, 300);
        });
    });
    
    // Close suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !suggestions?.contains(e.target)) {
            hideSuggestions();
        }
    });
    
    // Keyboard navigation for suggestions
    searchInput.addEventListener('keydown', function(e) {
        if (!suggestions || !suggestions.classList.contains('show')) return;
        
        const suggestionItems = suggestions.querySelectorAll('.search-suggestion');
        let currentIndex = Array.from(suggestionItems).findIndex(item => 
            item.classList.contains('selected')
        );
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                currentIndex = Math.min(currentIndex + 1, suggestionItems.length - 1);
                updateSelectedSuggestion(suggestionItems, currentIndex);
                break;
            case 'ArrowUp':
                e.preventDefault();
                currentIndex = Math.max(currentIndex - 1, 0);
                updateSelectedSuggestion(suggestionItems, currentIndex);
                break;
            case 'Enter':
                e.preventDefault();
                const selected = suggestions.querySelector('.search-suggestion.selected');
                if (selected) {
                    selected.click();
                } else {
                    this.closest('form').submit();
                }
                break;
            case 'Escape':
                hideSuggestions();
                break;
        }
    });
    
    function updateSelectedSuggestion(items, index) {
        items.forEach((item, i) => {
            item.classList.toggle('selected', i === index);
        });
    }
    
    console.log('✅ Enhanced search initialized');
}

/**
 * View Toggle System with Smooth Transitions
 */
function initViewToggleSystem() {
    const toggleBtns = document.querySelectorAll('.view-toggle-btn');
    const grid = document.getElementById('datalogsGrid');
    
    if (!grid || toggleBtns.length === 0) return;
    
    console.log('👁️ Initializing view toggle system...');
    
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const newView = this.dataset.view;
            
            if (newView === DataLogsEnhanced.currentView) return;
            
            // Update button states
            toggleBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Animate view transition
            animateViewTransition(grid, DataLogsEnhanced.currentView, newView);
            
            // Update current view
            DataLogsEnhanced.currentView = newView;
            
            // Store preference
            localStorage.setItem('datalogViewPreference', newView);
            
            // Analytics tracking
            console.log(`📊 View changed to: ${newView}`);
        });
    });
    
    // Load saved view preference
    const savedView = localStorage.getItem('datalogViewPreference');
    if (savedView && savedView !== DataLogsEnhanced.currentView) {
        const btn = document.querySelector(`[data-view="${savedView}"]`);
        if (btn) {
            btn.click();
        }
    }
    
    function animateViewTransition(container, fromView, toView) {
        // Add transition class
        container.classList.add('view-transitioning');
        
        // Fade out
        container.style.opacity = '0.3';
        container.style.transform = 'scale(0.98)';
        
        setTimeout(() => {
            // Change layout
            container.className = `datalogs-grid datalogs-${toView}`;
            
            // Fade in
            container.style.opacity = '1';
            container.style.transform = 'scale(1)';
            
            // Remove transition class
            setTimeout(() => {
                container.classList.remove('view-transitioning');
            }, 300);
        }, 150);
    }
    
    console.log('✅ View toggle system initialized');
}

/**
 * Advanced Card Animation System
 */
function initCardAnimations() {
    const cards = document.querySelectorAll('.datalog-card');
    
    if (cards.length === 0) return;
    
    console.log('🎬 Initializing card animation system...');
    
    // Intersection Observer for entrance animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const cardObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCardEntrance(entry.target);
                cardObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Set up cards for animation
    cards.forEach((card, index) => {
        // Initial state
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px) scale(0.95)';
        card.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        
        // Observe for entrance animation
        cardObserver.observe(card);
        
        // Enhanced hover interactions
        enhanceCardInteractions(card);
    });
    
    function animateCardEntrance(card) {
        card.style.opacity = '1';
        card.style.transform = 'translateY(0) scale(1)';
    }
    
    function enhanceCardInteractions(card) {
        let hoverTimeout;
        
        card.addEventListener('mouseenter', function() {
            clearTimeout(hoverTimeout);
            
            // Enhance image if present
            const image = this.querySelector('.datalog-image img');
            if (image) {
                image.style.transform = 'scale(1.05)';
            }
            
            // Animate read more button
            const readBtn = this.querySelector('.read-more-btn');
            if (readBtn) {
                readBtn.style.transform = 'translateX(5px)';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            hoverTimeout = setTimeout(() => {
                const image = this.querySelector('.datalog-image img');
                if (image) {
                    image.style.transform = 'scale(1)';
                }
                
                const readBtn = this.querySelector('.read-more-btn');
                if (readBtn) {
                    readBtn.style.transform = 'translateX(0)';
                }
            }, 100);
        });
        
        // Click animation
        card.addEventListener('click', function(e) {
            // Don't animate if clicking on a link
            if (e.target.closest('a')) return;
            
            // Add click ripple effect
            createRippleEffect(this, e);
        });
    }
    
    console.log('✅ Card animation system initialized');
}

/**
 * Terminal Enhancements
 */
function initTerminalEnhancements() {
    const terminal = document.querySelector('.featured-terminal-container');
    
    if (!terminal) return;
    
    console.log('💻 Initializing terminal enhancements...');
    
    // Intersection Observer for terminal activation
    const terminalObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                activateTerminal(entry.target);
                terminalObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.3 });
    
    terminalObserver.observe(terminal);
    
    function activateTerminal(terminal) {
        terminal.classList.add('terminal-active');
        
        // Animate terminal buttons
        const buttons = terminal.querySelectorAll('.terminal-button');
        buttons.forEach((button, index) => {
            setTimeout(() => {
                button.style.animation = 'pulse 0.5s ease';
            }, index * 200);
        });
    }
    
    console.log('✅ Terminal enhancements initialized');
}

/**
 * Initialize Scroll Effects
 */
function initScrollEffects() {
    // Add scroll-triggered animations
    const animateElements = document.querySelectorAll('.stat-group, .filter-tag, .pagination-btn');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });
    
    animateElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(element);
    });
}

/**
 * Utility Functions
 */

// Throttle function for performance
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

// Create ripple effect
function createRippleEffect(element, event) {
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
        background: radial-gradient(circle, rgba(179, 157, 219, 0.3) 0%, transparent 70%);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s ease-out;
        pointer-events: none;
        z-index: 1;
    `;
    
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// Create notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--gradient-glass), rgba(7, 7, 18, 0.9);
        color: var(--color-text);
        padding: 1rem 1.5rem;
        border-radius: var(--border-radius-md);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        z-index: 9999;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
        font-family: var(--font-body);
        font-size: 0.9rem;
        max-width: 300px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    `;
    
    // Type-specific styling
    if (type === 'success') {
        notification.style.borderColor = 'rgba(165, 214, 167, 0.5)';
        notification.style.color = 'var(--color-mint)';
    } else if (type === 'error') {
        notification.style.borderColor = 'rgba(255, 138, 128, 0.5)';
        notification.style.color = 'var(--color-coral)';
    } else if (type === 'info') {
        notification.style.borderColor = 'rgba(38, 198, 218, 0.5)';
        notification.style.color = 'var(--color-teal)';
    }
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
    
    .view-transitioning {
        pointer-events: none;
    }
    
    .search-loading {
        position: relative;
    }
    
    .search-loading::after {
        content: '';
        position: absolute;
        right: 1rem;
        top: 50%;
        transform: translateY(-50%);
        width: 16px;
        height: 16px;
        border: 2px solid rgba(179, 157, 219, 0.3);
        border-top: 2px solid var(--color-lavender);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    .category-loading {
        opacity: 0.6;
        pointer-events: none;
    }
    
    .search-suggestion.selected {
        background: rgba(179, 157, 219, 0.15);
        color: var(--color-lavender);
    }
    
    .suggestion-content {
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
    }
    
    .suggestion-category {
        font-size: 0.7rem;
        color: var(--color-text-tertiary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .suggestion-text mark {
        background: rgba(179, 157, 219, 0.3);
        color: var(--color-lavender);
        padding: 0;
    }
    
    @keyframes spin {
        0% { transform: translateY(-50%) rotate(0deg); }
        100% { transform: translateY(-50%) rotate(360deg); }
    }
`;
document.head.appendChild(style);

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initEnhancedDataLogs);
} else {
    initEnhancedDataLogs();
}

// Export for global access
window.DataLogsEnhanced = DataLogsEnhanced;
window.initEnhancedDataLogs = initEnhancedDataLogs;