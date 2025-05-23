/**
 * AURA Navigation Components
 * Advanced User Repository & Archive - Navigation System JavaScript
 * Version: 1.0.1
 */

// Navigation System State
const AURANavigation = {
    initialized: false,
    mobileMenuOpen: false,
    scrolled: false,
    activeSection: null
};

/**
 * Initialize AURA Navigation System
 */
function initAURANavigation() {
    console.log('🧭 AURA Navigation Initializing...');
    
    // Initialize core navigation features
    initMobileMenu();
    initScrollEffects();
    initActiveNavigation();
    initSmoothScrolling();
    initBreadcrumbs();
    
    // Mark as initialized
    AURANavigation.initialized = true;
    console.log('✅ AURA Navigation Online');
}

/**
 * Mobile Menu Functionality
 */
function initMobileMenu() {
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const navbar = document.querySelector('.navbar-nav');
    const navLinks = document.querySelectorAll('.nav-link');
    
    if (!mobileToggle || !navbar) return;
    
    // Toggle mobile menu
    mobileToggle.addEventListener('click', function() {
        toggleMobileMenu();
    });
    
    // Close mobile menu when clicking nav links
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 991) {
                closeMobileMenu();
            }
        });
    });
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        if (AURANavigation.mobileMenuOpen && 
            !navbar.contains(event.target) && 
            !mobileToggle.contains(event.target)) {
            closeMobileMenu();
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', debounce(function() {
        if (window.innerWidth > 991 && AURANavigation.mobileMenuOpen) {
            closeMobileMenu();
        }
    }, 250));
}

/**
 * Toggle mobile menu state
 */
function toggleMobileMenu() {
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const navbar = document.querySelector('.navbar-nav');
    
    if (AURANavigation.mobileMenuOpen) {
        closeMobileMenu();
    } else {
        openMobileMenu();
    }
}

/**
 * Open mobile menu
 */
function openMobileMenu() {
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const navbar = document.querySelector('.navbar-nav');
    
    if (mobileToggle && navbar) {
        mobileToggle.classList.add('active');
        navbar.classList.add('active');
        AURANavigation.mobileMenuOpen = true;
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        // Animate menu items
        const navLinks = navbar.querySelectorAll('.nav-link');
        navLinks.forEach((link, index) => {
            link.style.opacity = '0';
            link.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                link.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                link.style.opacity = '1';
                link.style.transform = 'translateX(0)';
            }, index * 100);
        });
    }
}

/**
 * Close mobile menu
 */
function closeMobileMenu() {
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const navbar = document.querySelector('.navbar-nav');
    
    if (mobileToggle && navbar) {
        mobileToggle.classList.remove('active');
        navbar.classList.remove('active');
        AURANavigation.mobileMenuOpen = false;
        
        // Restore body scroll
        document.body.style.overflow = '';
    }
}

/**
 * Scroll Effects for Navbar
 */
function initScrollEffects() {
    const navbar = document.querySelector('.aura-navbar');
    if (!navbar) return;
    
    function handleScroll() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const shouldBeScrolled = scrollTop > 50;
        
        if (shouldBeScrolled !== AURANavigation.scrolled) {
            AURANavigation.scrolled = shouldBeScrolled;
            
            if (shouldBeScrolled) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        }
    }
    
    // Throttle scroll events for performance
    window.addEventListener('scroll', throttle(handleScroll, 16));
    
    // Initial check
    handleScroll();
}

/**
 * Active Navigation State Management
 */
function initActiveNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const currentPath = window.location.pathname;
    
    // Remove all active states
    navLinks.forEach(link => {
        link.classList.remove('active');
    });
    
    // Set active state based on current path
    navLinks.forEach(link => {
        const linkPath = new URL(link.href).pathname;
        
        // Exact match or partial match for nested pages
        if (linkPath === currentPath || 
            (linkPath !== '/' && currentPath.startsWith(linkPath))) {
            link.classList.add('active');
        }
    });
}

/**
 * Smooth Scrolling for Anchor Links
 */
function initSmoothScrolling() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            const href = this.getAttribute('href');
            
            // Skip if it's just "#"
            if (href === '#') return;
            
            const target = document.querySelector(href);
            if (target) {
                event.preventDefault();
                
                // Close mobile menu if open
                if (AURANavigation.mobileMenuOpen) {
                    closeMobileMenu();
                }
                
                // Calculate offset for fixed navbar
                const navbarHeight = document.querySelector('.aura-navbar')?.offsetHeight || 80;
                const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - navbarHeight - 20;
                
                // Smooth scroll with custom easing
                smoothScrollTo(targetPosition);
                
                // Update URL without jumping
                if (history.pushState) {
                    history.pushState(null, null, href);
                }
            }
        });
    });
}

/**
 * Enhanced smooth scroll function
 */
function smoothScrollTo(targetPosition) {
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    const duration = Math.min(Math.abs(distance) / 2, 800); // Max 800ms
    let start = null;
    
    function animation(currentTime) {
        if (start === null) start = currentTime;
        const timeElapsed = currentTime - start;
        const progress = Math.min(timeElapsed / duration, 1);
        
        // Easing function (ease-out-quart)
        const ease = 1 - Math.pow(1 - progress, 4);
        
        window.scrollTo(0, startPosition + distance * ease);
        
        if (timeElapsed < duration) {
            requestAnimationFrame(animation);
        }
    }
    
    requestAnimationFrame(animation);
}

/**
 * Breadcrumb Navigation Enhancement
 */
function initBreadcrumbs() {
    const breadcrumbs = document.querySelector('.aura-breadcrumbs');
    if (!breadcrumbs) return;
    
    // Add hover effects to breadcrumb items
    const breadcrumbItems = breadcrumbs.querySelectorAll('.breadcrumb-item');
    
    breadcrumbItems.forEach(item => {
        if (item.href) {
            item.addEventListener('mouseenter', function() {
                this.style.transform = 'translateX(3px)';
            });
            
            item.addEventListener('mouseleave', function() {
                this.style.transform = 'translateX(0)';
            });
        }
    });
}

/**
 * Section Observer for Active Navigation
 */
function initSectionObserver() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link[href^="#"]');
    
    if (sections.length === 0) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const sectionId = entry.target.id;
                AURANavigation.activeSection = sectionId;
                
                // Update active nav link
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }, {
        threshold: 0.3,
        rootMargin: '-80px 0px'
    });
    
    sections.forEach(section => {
        observer.observe(section);
    });
}

/**
 * Navigation Search Functionality
 */
function initNavigationSearch() {
    const searchInput = document.querySelector('.nav-search-input');
    const searchResults = document.querySelector('.nav-search-results');
    const searchableItems = [
        { title: 'Dashboard', url: '/', category: 'Navigation' },
        { title: 'DataLogs', url: '/blog/', category: 'Navigation' },
        { title: 'Systems', url: '/projects/', category: 'Navigation' },
        { title: 'Profile', url: '/about/', category: 'Navigation' },
        { title: 'Contact', url: '/contact/', category: 'Navigation' }
    ];
    
    if (!searchInput) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            if (query.length > 0) {
                showSearchResults(query, searchableItems);
            } else {
                hideSearchResults();
            }
        }, 300);
    });
    
    // Close search results when clicking outside
    document.addEventListener('click', function(event) {
        if (!searchInput.contains(event.target) && 
            !searchResults?.contains(event.target)) {
            hideSearchResults();
        }
    });
}

/**
 * Show search results
 */
function showSearchResults(query, items) {
    const searchResults = document.querySelector('.nav-search-results');
    if (!searchResults) return;
    
    const filteredItems = items.filter(item => 
        item.title.toLowerCase().includes(query) ||
        item.category.toLowerCase().includes(query)
    );
    
    if (filteredItems.length > 0) {
        const resultsHTML = filteredItems.map(item => `
            <a href="${item.url}" class="search-result-item">
                <div class="search-result-title">${item.title}</div>
                <div class="search-result-category">${item.category}</div>
            </a>
        `).join('');
        
        searchResults.innerHTML = resultsHTML;
        searchResults.classList.add('active');
    } else {
        searchResults.innerHTML = '<div class="search-no-results">No results found</div>';
        searchResults.classList.add('active');
    }
}

/**
 * Hide search results
 */
function hideSearchResults() {
    const searchResults = document.querySelector('.nav-search-results');
    if (searchResults) {
        searchResults.classList.remove('active');
    }
}

/**
 * Keyboard Navigation Enhancement
 */
function initKeyboardNavigation() {
    document.addEventListener('keydown', function(event) {
        // ESC key closes mobile menu
        if (event.key === 'Escape' && AURANavigation.mobileMenuOpen) {
            closeMobileMenu();
        }
        
        // Alt + M toggles mobile menu
        if (event.altKey && event.key === 'm') {
            event.preventDefault();
            toggleMobileMenu();
        }
        
        // Arrow key navigation in mobile menu
        if (AURANavigation.mobileMenuOpen && (event.key === 'ArrowUp' || event.key === 'ArrowDown')) {
            event.preventDefault();
            navigateMenuWithKeys(event.key);
        }
    });
}

/**
 * Navigate menu items with arrow keys
 */
function navigateMenuWithKeys(direction) {
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const activeElement = document.activeElement;
    const currentIndex = Array.from(navLinks).indexOf(activeElement);
    
    let nextIndex;
    if (direction === 'ArrowDown') {
        nextIndex = currentIndex + 1 >= navLinks.length ? 0 : currentIndex + 1;
    } else {
        nextIndex = currentIndex - 1 < 0 ? navLinks.length - 1 : currentIndex - 1;
    }
    
    navLinks[nextIndex].focus();
}

/**
 * Footer Enhancement
 */
function initFooterEnhancements() {
    // Animate footer links on hover
    const footerLinks = document.querySelectorAll('.footer-link');
    
    footerLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(5px)';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0)';
        });
    });
    
    // Network node hover effects
    const networkNodes = document.querySelectorAll('.network-node');
    
    networkNodes.forEach(node => {
        node.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        node.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

/**
 * Navigation Performance Monitoring
 */
function initNavigationPerformance() {
    // Monitor navigation performance
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(() => {
                const navigation = performance.getEntriesByType('navigation')[0];
                if (navigation) {
                    console.log('🚀 Navigation Performance:', {
                        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
                        totalTime: navigation.loadEventEnd - navigation.fetchStart
                    });
                }
            }, 0);
        });
    }
}

/**
 * Utility Functions
 */

/**
 * Debounce function to limit function calls
 */
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

/**
 * Throttle function to limit function execution rate
 */
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

/**
 * Get current page information
 */
function getCurrentPageInfo() {
    return {
        path: window.location.pathname,
        hash: window.location.hash,
        search: window.location.search,
        title: document.title
    };
}

/**
 * Navigation Analytics
 */
function trackNavigation(from, to, method = 'click') {
    // Basic navigation tracking
    if (window.gtag) {
        gtag('event', 'navigation', {
            'event_category': 'Navigation',
            'event_label': `${from} -> ${to}`,
            'custom_method': method
        });
    }
    
    console.log(`🧭 Navigation: ${from} -> ${to} (${method})`);
}

/**
 * Navigation State Management
 */
const NavigationState = {
    history: [],
    current: null,
    
    push(pageInfo) {
        this.history.push(this.current);
        this.current = pageInfo;
        
        // Keep only last 10 entries
        if (this.history.length > 10) {
            this.history.shift();
        }
    },
    
    back() {
        if (this.history.length > 0) {
            return this.history.pop();
        }
        return null;
    },
    
    getCurrent() {
        return this.current;
    }
};

/**
 * Enhanced Navigation Features
 */
function initEnhancedNavigation() {
    // Initialize navigation state
    NavigationState.push(getCurrentPageInfo());
    
    // Track all navigation events
    const navLinks = document.querySelectorAll('a[href]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            const from = NavigationState.getCurrent()?.path || 'unknown';
            const to = this.getAttribute('href');
            
            // Track navigation
            trackNavigation(from, to, 'click');
            
            // Update navigation state for internal links
            if (!this.hasAttribute('target') && !to.startsWith('http')) {
                setTimeout(() => {
                    NavigationState.push(getCurrentPageInfo());
                }, 100);
            }
        });
    });
}

/**
 * Progressive Enhancement for Navigation
 */
function initProgressiveEnhancement() {
    // Add CSS classes for JavaScript-enabled features
    document.documentElement.classList.add('js-enabled');
    
    // Add navigation-specific classes
    const navbar = document.querySelector('.aura-navbar');
    if (navbar) {
        navbar.classList.add('enhanced');
    }
    
    // Add loading indicators for slow connections
    if ('connection' in navigator) {
        const connection = navigator.connection;
        if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
            document.body.classList.add('slow-connection');
        }
    }
}

/**
 * Accessibility Enhancements
 */
function initAccessibilityEnhancements() {
    // Skip to main content link
    const skipLink = document.querySelector('.skip-to-main');
    if (skipLink) {
        skipLink.addEventListener('click', function(event) {
            event.preventDefault();
            const mainContent = document.querySelector('main') || document.querySelector('#main-content');
            if (mainContent) {
                mainContent.focus();
                mainContent.scrollIntoView();
            }
        });
    }
    
    // Announce page changes to screen readers
    const announcer = document.createElement('div');
    announcer.setAttribute('aria-live', 'polite');
    announcer.setAttribute('aria-atomic', 'true');
    announcer.className = 'sr-only';
    document.body.appendChild(announcer);
    
    // Announce navigation changes
    window.addEventListener('popstate', function() {
        announcer.textContent = `Navigated to ${document.title}`;
    });
    
    // Enhanced focus management
    let focusedBeforeModal = null;
    
    // Trap focus in mobile menu
    document.addEventListener('keydown', function(event) {
        if (AURANavigation.mobileMenuOpen && event.key === 'Tab') {
            trapFocus(event, '.navbar-nav');
        }
    });
}

/**
 * Trap focus within a container
 */
function trapFocus(event, containerSelector) {
    const container = document.querySelector(containerSelector);
    if (!container) return;
    
    const focusableElements = container.querySelectorAll(
        'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select'
    );
    
    const firstFocusableElement = focusableElements[0];
    const lastFocusableElement = focusableElements[focusableElements.length - 1];
    
    if (event.shiftKey) {
        if (document.activeElement === firstFocusableElement) {
            lastFocusableElement.focus();
            event.preventDefault();
        }
    } else {
        if (document.activeElement === lastFocusableElement) {
            firstFocusableElement.focus();
            event.preventDefault();
        }
    }
}

/**
 * Navigation Error Handling
 */
function initNavigationErrorHandling() {
    // Handle navigation errors gracefully
    window.addEventListener('error', function(event) {
        if (event.target.tagName === 'A') {
            console.warn('Navigation link error:', event.target.href);
            // Could show user-friendly message or fallback
        }
    });
    
    // Handle offline navigation
    window.addEventListener('offline', function() {
        const navbar = document.querySelector('.aura-navbar');
        if (navbar) {
            navbar.classList.add('offline');
        }
        
        // Disable external links when offline
        const externalLinks = document.querySelectorAll('a[href^="http"]');
        externalLinks.forEach(link => {
            link.style.opacity = '0.5';
            link.style.pointerEvents = 'none';
        });
    });
    
    window.addEventListener('online', function() {
        const navbar = document.querySelector('.aura-navbar');
        if (navbar) {
            navbar.classList.remove('offline');
        }
        
        // Re-enable external links when online
        const externalLinks = document.querySelectorAll('a[href^="http"]');
        externalLinks.forEach(link => {
            link.style.opacity = '';
            link.style.pointerEvents = '';
        });
    });
}

/**
 * Initialize all navigation features
 */
function initAllNavigationFeatures() {
    initAURANavigation();
    initSectionObserver();
    initNavigationSearch();
    initKeyboardNavigation();
    initFooterEnhancements();
    initNavigationPerformance();
    initEnhancedNavigation();
    initProgressiveEnhancement();
    initAccessibilityEnhancements();
    initNavigationErrorHandling();
}

/**
 * Export functions for global access
 */
window.AURANavigation = AURANavigation;
window.initAURANavigation = initAURANavigation;
window.toggleMobileMenu = toggleMobileMenu;
window.closeMobileMenu = closeMobileMenu;
window.smoothScrollTo = smoothScrollTo;
window.initAllNavigationFeatures = initAllNavigationFeatures;

// Auto-initialize navigation if DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAllNavigationFeatures);
} else {
    initAllNavigationFeatures();
}