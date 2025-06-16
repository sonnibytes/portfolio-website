/**
 * AURA Navigation System JavaScript
 * Advanced User Repository & Archive - Navigation Components
 * Version: 1.0.1
 */

// Navigation System State
const NavigationSystem = {
    initialized: false,
    mobileMenuOpen: false,
    currentSubNav: null,
    scrollPosition: 0
};

/**
 * Initialize Navigation System
 */
function initNavigationSystem() {
    console.log('🧭 Navigation System Initializing...');
    
    // Initialize core navigation components
    initMainNavigation();
    initMobileMenu();
    initSubNavigation();
    initScrollEffects();
    initKeyboardNavigation();
    
    // Mark as initialized
    NavigationSystem.initialized = true;
    console.log('✅ Navigation System Online');
}

/**
 * Initialize Main Navigation
 */
function initMainNavigation() {
    const navbar = document.querySelector('.aura-navbar');
    const navLinks = document.querySelectorAll('.nav-link');
    
    if (!navbar) return;
    
    // Add active state management
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Add loading effect
            this.classList.add('nav-loading');
            
            // Remove loading after navigation
            setTimeout(() => {
                this.classList.remove('nav-loading');
            }, 1000);
        });
        
        // Enhanced hover effects
        link.addEventListener('mouseenter', function() {
            this.classList.add('nav-scan-line');
        });
        
        link.addEventListener('mouseleave', function() {
            this.classList.remove('nav-scan-line');
        });
    });
    
    // Brand click effect
    const brand = document.querySelector('.navbar-brand');
    if (brand) {
        brand.addEventListener('click', function() {
            const brandIcon = this.querySelector('.brand-icon');
            if (brandIcon) {
                brandIcon.style.animation = 'none';
                setTimeout(() => {
                    brandIcon.style.animation = 'pulse 3s ease-in-out infinite';
                }, 10);
            }
        });
    }
}

/**
 * Initialize Mobile Menu
 */
function initMobileMenu() {
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const navbar = document.querySelector('.navbar-nav');
    
    if (!mobileToggle || !navbar) return;
    
    mobileToggle.addEventListener('click', function() {
        NavigationSystem.mobileMenuOpen = !NavigationSystem.mobileMenuOpen;
        
        // Toggle classes
        this.classList.toggle('active');
        navbar.classList.toggle('active');
        
        // Prevent body scroll when menu is open
        if (NavigationSystem.mobileMenuOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
        
        // Add accessibility attributes
        this.setAttribute('aria-expanded', NavigationSystem.mobileMenuOpen);
        navbar.setAttribute('aria-hidden', !NavigationSystem.mobileMenuOpen);
    });
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (NavigationSystem.mobileMenuOpen && 
            !mobileToggle.contains(e.target) && 
            !navbar.contains(e.target)) {
            closeMobileMenu();
        }
    });
    
    // Close mobile menu on nav link click
    const navLinks = navbar.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', closeMobileMenu);
    });
}

/**
 * Close Mobile Menu
 */
function closeMobileMenu() {
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const navbar = document.querySelector('.navbar-nav');
    
    if (mobileToggle && navbar && NavigationSystem.mobileMenuOpen) {
        NavigationSystem.mobileMenuOpen = false;
        mobileToggle.classList.remove('active');
        navbar.classList.remove('active');
        document.body.style.overflow = '';
        
        mobileToggle.setAttribute('aria-expanded', false);
        navbar.setAttribute('aria-hidden', true);
    }
}

/**
 * Initialize Sub-Navigation
 */
function initSubNavigation() {
    const subNavs = document.querySelectorAll('.datalogs-subnav, .systems-subnav');
    
    subNavs.forEach(subNav => {
        const subNavLinks = subNav.querySelectorAll('.subnav-link');
        const actionBtns = subNav.querySelectorAll('.subnav-action-btn');
        
        // Sub-navigation link interactions
        subNavLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                // Add loading effect
                this.classList.add('nav-loading');
                
                // Update active state
                subNavLinks.forEach(l => l.classList.remove('active'));
                this.classList.add('active');
            });
            
            // Enhanced hover effects
            link.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
            });
            
            link.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });
        
        // Action button interactions
        actionBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                // Add click animation
                this.style.transform = 'translateY(-1px) scale(0.95)';
                setTimeout(() => {
                    this.style.transform = 'translateY(-1px) scale(1)';
                }, 150);
            });
        });
        
        // Store current subnav type
        if (subNav.classList.contains('datalogs-subnav')) {
            NavigationSystem.currentSubNav = 'datalogs';
        } else if (subNav.classList.contains('systems-subnav')) {
            NavigationSystem.currentSubNav = 'systems';
        }
    });
    
    // Initialize real-time stats updates
    updateSubNavStats();
    setInterval(updateSubNavStats, 30000); // Update every 30 seconds
}

/**
 * Update Sub-Navigation Stats
 */
function updateSubNavStats() {
    const statValues = document.querySelectorAll('.stat-value');
    
    statValues.forEach(stat => {
        const currentValue = parseInt(stat.textContent) || 0;
        
        // Simulate minor fluctuations for demo purposes
        if (Math.random() > 0.7) { // 30% chance to update
            const change = Math.random() > 0.5 ? 1 : -1;
            const newValue = Math.max(0, currentValue + change);
            
            if (newValue !== currentValue) {
                animateStatChange(stat, currentValue, newValue);
            }
        }
    });
}

/**
 * Animate Stat Value Change
 */
function animateStatChange(element, fromValue, toValue) {
    element.style.color = 'var(--color-yellow)';
    element.style.transform = 'scale(1.1)';
    
    // Animate the number change
    const duration = 500;
    const steps = 10;
    const stepValue = (toValue - fromValue) / steps;
    let currentStep = 0;
    
    const interval = setInterval(() => {
        currentStep++;
        const currentValue = Math.round(fromValue + (stepValue * currentStep));
        element.textContent = currentValue;
        
        if (currentStep >= steps) {
            clearInterval(interval);
            
            // Reset styling
            setTimeout(() => {
                element.style.color = '';
                element.style.transform = '';
            }, 200);
        }
    }, duration / steps);
}

/**
 * Initialize Scroll Effects
 */
function initScrollEffects() {
    const navbar = document.querySelector('.aura-navbar');
    const subNavs = document.querySelectorAll('.datalogs-subnav, .systems-subnav');
    
    if (!navbar) return;
    
    let lastScrollTop = 0;
    let ticking = false;
    
    function updateNavOnScroll() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollDirection = scrollTop > lastScrollTop ? 'down' : 'up';
        
        // Navbar effects based on scroll
        if (scrollTop > 100) {
            navbar.style.background = `
                linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%),
                rgba(7, 7, 18, 0.95)
            `;
            navbar.style.backdropFilter = 'blur(30px)';
            navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
        } else {
            navbar.style.background = `
                linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%),
                rgba(7, 7, 18, 0.9)
            `;
            navbar.style.backdropFilter = 'blur(25px)';
            navbar.style.boxShadow = '';
        }
        
        // Sub-navigation effects
        subNavs.forEach(subNav => {
            if (scrollTop > 200 && scrollDirection === 'down') {
                subNav.style.transform = 'translateY(-100%)';
                subNav.style.opacity = '0';
            } else {
                subNav.style.transform = 'translateY(0)';
                subNav.style.opacity = '1';
            }
        });
        
        lastScrollTop = scrollTop;
        NavigationSystem.scrollPosition = scrollTop;
        ticking = false;
    }
    
    function requestScrollUpdate() {
        if (!ticking) {
            requestAnimationFrame(updateNavOnScroll);
            ticking = true;
        }
    }
    
    // Throttled scroll listener
    window.addEventListener('scroll', requestScrollUpdate, { passive: true });
}

/**
 * Initialize Keyboard Navigation
 */
function initKeyboardNavigation() {
    document.addEventListener('keydown', function(e) {
        // ESC to close mobile menu
        if (e.key === 'Escape' && NavigationSystem.mobileMenuOpen) {
            closeMobileMenu();
        }
        
        // Tab navigation enhancement
        if (e.key === 'Tab') {
            document.body.classList.add('keyboard-navigation');
        }
        
        // Quick navigation shortcuts
        if (e.altKey || e.ctrlKey) {
            switch(e.key) {
                case 'h':
                    e.preventDefault();
                    navigateToHome();
                    break;
                case 'd':
                    e.preventDefault();
                    navigateToDataLogs();
                    break;
                case 's':
                    e.preventDefault();
                    navigateToSystems();
                    break;
                case 'p':
                    e.preventDefault();
                    navigateToProfile();
                    break;
                case 'c':
                    e.preventDefault();
                    navigateToContact();
                    break;
            }
        }
    });
    
    // Remove keyboard navigation class on mouse interaction
    document.addEventListener('mousedown', () => {
        document.body.classList.remove('keyboard-navigation');
    });
}

/**
 * Navigation Helper Functions
 */
function navigateToHome() {
    const homeLink = document.querySelector('a[href*="home"], a[href="/"]');
    if (homeLink) homeLink.click();
}

function navigateToDataLogs() {
    const datalogsLink = document.querySelector('a[href*="blog"], a[href*="datalog"]');
    if (datalogsLink) datalogsLink.click();
}

function navigateToSystems() {
    const systemsLink = document.querySelector('a[href*="projects"], a[href*="systems"]');
    if (systemsLink) systemsLink.click();
}

function navigateToProfile() {
    const profileLink = document.querySelector('a[href*="about"], a[href*="profile"]');
    if (profileLink) profileLink.click();
}

function navigateToContact() {
    const contactLink = document.querySelector('a[href*="contact"], a[href*="communication"]');
    if (contactLink) contactLink.click();
}

/**
 * Initialize Dropdown Menus
 */
function initDropdownMenus() {
    const dropdowns = document.querySelectorAll('.nav-dropdown');
    
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (!toggle || !menu) return;
        
        let hoverTimeout;
        
        // Show dropdown on hover
        dropdown.addEventListener('mouseenter', function() {
            clearTimeout(hoverTimeout);
            menu.style.opacity = '1';
            menu.style.visibility = 'visible';
            menu.style.transform = 'translateY(0)';
        });
        
        // Hide dropdown on leave
        dropdown.addEventListener('mouseleave', function() {
            hoverTimeout = setTimeout(() => {
                menu.style.opacity = '0';
                menu.style.visibility = 'hidden';
                menu.style.transform = 'translateY(-10px)';
            }, 150);
        });
        
        // Keyboard navigation for dropdowns
        toggle.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const isVisible = menu.style.visibility === 'visible';
                
                if (isVisible) {
                    menu.style.opacity = '0';
                    menu.style.visibility = 'hidden';
                    menu.style.transform = 'translateY(-10px)';
                } else {
                    menu.style.opacity = '1';
                    menu.style.visibility = 'visible';
                    menu.style.transform = 'translateY(0)';
                    
                    // Focus first item
                    const firstItem = menu.querySelector('.dropdown-item');
                    if (firstItem) firstItem.focus();
                }
            }
        });
        
        // Handle dropdown item navigation
        const dropdownItems = menu.querySelectorAll('.dropdown-item');
        dropdownItems.forEach((item, index) => {
            item.addEventListener('keydown', function(e) {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    const nextItem = dropdownItems[index + 1];
                    if (nextItem) nextItem.focus();
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    const prevItem = dropdownItems[index - 1];
                    if (prevItem) {
                        prevItem.focus();
                    } else {
                        toggle.focus();
                    }
                } else if (e.key === 'Escape') {
                    menu.style.opacity = '0';
                    menu.style.visibility = 'hidden';
                    menu.style.transform = 'translateY(-10px)';
                    toggle.focus();
                }
            });
        });
    });
}

/**
 * Initialize Breadcrumb Navigation
 */
function initBreadcrumbNavigation() {
    const breadcrumbs = document.querySelectorAll('.breadcrumb-nav');
    
    breadcrumbs.forEach(breadcrumb => {
        const items = breadcrumb.querySelectorAll('.breadcrumb-item');
        
        items.forEach((item, index) => {
            item.addEventListener('click', function(e) {
                // Add loading effect for non-active items
                if (!this.classList.contains('active')) {
                    this.style.opacity = '0.6';
                    this.innerHTML += ' <i class="fas fa-spinner fa-spin" style="margin-left: 0.25rem; font-size: 0.7rem;"></i>';
                }
            });
        });
    });
}

/**
 * Initialize Navigation Search
 */
function initNavigationSearch() {
    const searchToggle = document.querySelector('.nav-search-toggle');
    const searchOverlay = document.querySelector('.nav-search-overlay');
    const searchInput = document.querySelector('.nav-search-input');
    const searchClose = document.querySelector('.nav-search-close');
    
    if (!searchToggle || !searchOverlay) return;
    
    // Open search overlay
    searchToggle.addEventListener('click', function(e) {
        e.preventDefault();
        openSearchOverlay();
    });
    
    // Close search overlay
    if (searchClose) {
        searchClose.addEventListener('click', function() {
            closeSearchOverlay();
        });
    }
    
    // Close on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && searchOverlay.classList.contains('active')) {
            closeSearchOverlay();
        }
    });
    
    // Close on overlay click
    searchOverlay.addEventListener('click', function(e) {
        if (e.target === this) {
            closeSearchOverlay();
        }
    });
    
    function openSearchOverlay() {
        searchOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        if (searchInput) {
            setTimeout(() => {
                searchInput.focus();
            }, 300);
        }
    }
    
    function closeSearchOverlay() {
        searchOverlay.classList.remove('active');
        document.body.style.overflow = '';
        
        if (searchInput) {
            searchInput.value = '';
        }
    }
}

/**
 * Initialize Status Indicators
 */
function initStatusIndicators() {
    const statusIndicators = document.querySelectorAll('.status-indicator');
    
    statusIndicators.forEach(indicator => {
        // Add random pulse variations for more realistic effect
        const pulseDelay = Math.random() * 2;
        indicator.style.animationDelay = `${pulseDelay}s`;
        
        // Add tooltip functionality
        const tooltip = indicator.getAttribute('title') || indicator.getAttribute('data-tooltip');
        if (tooltip) {
            indicator.addEventListener('mouseenter', function() {
                showTooltip(this, tooltip);
            });
            
            indicator.addEventListener('mouseleave', function() {
                hideTooltip();
            });
        }
    });
}


/**
* Initialize Real-time Clock Updates
*/
function initRealtimeClock() {
  const timestampElements = document.querySelectorAll('[data-timestamp]');
  
  function updateTimestamps() {
      const now = new Date();
      
      timestampElements.forEach(element => {
          const format = element.dataset.timestamp || 'datetime';
          
          switch (format) {
              case 'time':
                  element.textContent = now.toLocaleTimeString('en-US', { 
                      hour12: false, 
                      timeZone: 'UTC' 
                  }) + ' UTC';
                  break;
              case 'date':
                  element.textContent = now.toISOString().split('T')[0];
                  break;
              case 'datetime':
              default:
                  element.textContent = now.toISOString().slice(0, 19).replace('T', ' ') + ' UTC';
                  break;
          }
      });
  }
  
  // Update immediately and then every second
  updateTimestamps();
  setInterval(updateTimestamps, 1000);
}

/**
 * Show Tooltip
 */
function showTooltip(element, text) {
    let tooltip = document.querySelector('.nav-tooltip');
    
    if (!tooltip) {
        tooltip = document.createElement('div');
        tooltip.className = 'nav-tooltip';
        tooltip.style.cssText = `
            position: absolute;
            background: rgba(7, 7, 18, 0.9);
            color: var(--color-text);
            padding: 0.5rem;
            border-radius: var(--border-radius-sm);
            font-size: 0.8rem;
            font-family: var(--font-code);
            z-index: 9999;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            opacity: 0;
            transition: opacity 0.2s ease;
            pointer-events: none;
        `;
        document.body.appendChild(tooltip);
    }
    
    tooltip.textContent = text;
    
    const rect = element.getBoundingClientRect();
    tooltip.style.top = `${rect.bottom + 8}px`;
    tooltip.style.left = `${rect.left + (rect.width / 2)}px`;
    tooltip.style.transform = 'translateX(-50%)';
    tooltip.style.opacity = '1';
}

/**
 * Hide Tooltip
 */
function hideTooltip() {
    const tooltip = document.querySelector('.nav-tooltip');
    if (tooltip) {
        tooltip.style.opacity = '0';
    }
}

/**
 * Initialize Performance Monitoring
 */
function initPerformanceMonitoring() {
    // Monitor navigation performance
    const navItems = document.querySelectorAll('.nav-link, .subnav-link');
    
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            const startTime = performance.now();
            const href = this.getAttribute('href');
            
            // Log navigation performance (for development)
            setTimeout(() => {
                const endTime = performance.now();
                const duration = endTime - startTime;
                
                if (duration > 100) {
                    console.log(`Navigation to ${href} took ${duration.toFixed(2)}ms`);
                }
            }, 0);
        });
    });
}

/**
 * Initialize Theme Detection
 */
function initThemeDetection() {
    // Listen for theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    function handleThemeChange(e) {
        if (e.matches) {
            document.body.classList.add('dark-theme');
        } else {
            document.body.classList.remove('dark-theme');
        }
    }
    
    mediaQuery.addListener(handleThemeChange);
    handleThemeChange(mediaQuery);
}

/**
 * Initialize Accessibility Features
 */
function initAccessibilityFeatures() {
    // Add skip navigation link
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'skip-nav-link';
    skipLink.style.cssText = `
        position: absolute;
        top: -40px;
        left: 6px;
        background: var(--color-teal);
        color: var(--color-text);
        padding: 8px;
        text-decoration: none;
        border-radius: 4px;
        z-index: 9999;
        transition: top 0.3s ease;
    `;
    
    skipLink.addEventListener('focus', function() {
        this.style.top = '6px';
    });
    
    skipLink.addEventListener('blur', function() {
        this.style.top = '-40px';
    });
    
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Add ARIA labels where missing
    const navItems = document.querySelectorAll('.nav-link, .subnav-link');
    navItems.forEach(item => {
        if (!item.getAttribute('aria-label') && !item.querySelector('.nav-text')) {
            const text = item.textContent.trim();
            if (text) {
                item.setAttribute('aria-label', text);
            }
        }
    });
    
    // Add role attributes
    const navbar = document.querySelector('.aura-navbar');
    if (navbar && !navbar.getAttribute('role')) {
        navbar.setAttribute('role', 'navigation');
        navbar.setAttribute('aria-label', 'Main navigation');
    }
    
    const subNavs = document.querySelectorAll('.datalogs-subnav, .systems-subnav');
    subNavs.forEach(subNav => {
        if (!subNav.getAttribute('role')) {
            subNav.setAttribute('role', 'navigation');
            subNav.setAttribute('aria-label', 'Secondary navigation');
        }
    });
}

/**
 * Handle Window Resize
 */
function handleResize() {
    // Close mobile menu on resize to desktop
    if (window.innerWidth > 991 && NavigationSystem.mobileMenuOpen) {
        closeMobileMenu();
    }
    
    // Update dropdown positions
    const dropdownMenus = document.querySelectorAll('.dropdown-menu');
    dropdownMenus.forEach(menu => {
        menu.style.opacity = '0';
        menu.style.visibility = 'hidden';
        menu.style.transform = 'translateY(-10px)';
    });
}

/**
 * Navigation System Utils
 */
const NavigationUtils = {
    // Get current page type
    getCurrentPageType() {
        const path = window.location.pathname;
        
        if (path.includes('/blog/') || path.includes('/datalog')) {
            return 'datalogs';
        } else if (path.includes('/projects/') || path.includes('/systems/')) {
            return 'systems';
        } else if (path.includes('/about/') || path.includes('/profile/')) {
            return 'profile';
        } else if (path.includes('/contact/')) {
            return 'contact';
        } else if (path === '/' || path.includes('/home/')) {
            return 'home';
        }
        
        return 'unknown';
    },
    
    // Update active navigation states
    updateActiveStates() {
        const currentPage = this.getCurrentPageType();
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            
            const href = link.getAttribute('href');
            if (href) {
                if ((currentPage === 'home' && href.includes('home')) ||
                    (currentPage === 'datalogs' && href.includes('blog')) ||
                    (currentPage === 'systems' && href.includes('projects')) ||
                    (currentPage === 'profile' && href.includes('about')) ||
                    (currentPage === 'contact' && href.includes('contact'))) {
                    link.classList.add('active');
                }
            }
        });
    },
    
    // Show loading state
    showLoading(element) {
        if (element) {
            element.classList.add('nav-loading');
        }
    },
    
    // Hide loading state
    hideLoading(element) {
        if (element) {
            element.classList.remove('nav-loading');
        }
    }
};

/**
 * Initialize Navigation System on DOM ready
 */
document.addEventListener('DOMContentLoaded', function() {
    initNavigationSystem();
    initDropdownMenus();
    initBreadcrumbNavigation();
    initNavigationSearch();
    initStatusIndicators();
    initRealtimeClock();
    initPerformanceMonitoring();
    initThemeDetection();
    initAccessibilityFeatures();
    
    // Update active states
    NavigationUtils.updateActiveStates();
    
    // Handle window resize
    window.addEventListener('resize', throttle(handleResize, 150));
    
    // Add keyboard shortcuts help for development
    if (console && console.log) {
        console.log(`
🧭 AURA Navigation Shortcuts:
   Alt/Ctrl + H - Home
   Alt/Ctrl + D - DataLogs
   Alt/Ctrl + S - Systems
   Alt/Ctrl + P - Profile
   Alt/Ctrl + C - Contact
   ESC - Close menus
        `);
    }
});

/**
 * Throttle function for performance
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
 * Export Navigation System for global access
 */
window.NavigationSystem = NavigationSystem;
window.NavigationUtils = NavigationUtils;
window.initNavigationSystem = initNavigationSystem;