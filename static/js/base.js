/**
 * AURA Portfolio - Base JavaScript
 * Advanced User Repository & Archive - Core System Functions
 * Version: 2.0.1 - Component Architecture
 */

// AURA System State
const AURA = {
  initialized: false,
  loadingComplete: false,
  components: {},
  settings: {
      loadingDuration: 7000,
      animationSpeed: 'normal',
      reducedMotion: false
  }
};

/**
* Initialize AURA System
* Main entry point for the AURA interface
*/
function initAURASystem() {
  console.log('🚀 AURA System Initializing...');
  
  // Check for reduced motion preference
  AURA.settings.reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  
  // Initialize core components
  initSystemMonitoring();
  initResponsiveSystem();
  initAccessibility();
  
  // Mark as initialized
  AURA.initialized = true;
  console.log('✅ AURA System Online');
}

/**
* System Monitoring and Status Updates
*/
function initSystemMonitoring() {
  // Update timestamps in real-time
  updateTimestamps();
  setInterval(updateTimestamps, 1000);
  
  // Monitor system performance
  monitorPerformance();
  
  // Update status indicators
  updateStatusIndicators();
}

/**
* Update all timestamp elements
*/
function updateTimestamps() {
  const timestampElements = document.querySelectorAll('[data-timestamp]');
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
  
  // Update footer timestamp if it exists
  const footerTimestamp = document.querySelector('.footer-timestamp span');
  if (footerTimestamp) {
      footerTimestamp.textContent = `Last Updated: ${now.toISOString().slice(0, 19).replace('T', ' ')} UTC`;
  }
}

/**
* Monitor system performance and update metrics
*/
function monitorPerformance() {
  // Simulate system metrics updates
  const metricElements = document.querySelectorAll('[data-metric]');
  
  metricElements.forEach(element => {
      const metricType = element.dataset.metric;
      
      switch (metricType) {
          case 'uptime':
              element.textContent = '99.7%';
              break;
          case 'response_time':
              // Simulate response time between 120-180ms
              const responseTime = Math.floor(Math.random() * 60) + 120;
              element.textContent = responseTime + 'ms';
              break;
          case 'memory_usage':
              // Simulate memory usage between 60-85%
              const memUsage = Math.floor(Math.random() * 25) + 60;
              element.textContent = memUsage + '%';
              break;
      }
  });
}

/**
* Update status indicators based on system state
*/
function updateStatusIndicators() {
  const statusIndicators = document.querySelectorAll('.status-indicator');
  
  statusIndicators.forEach(indicator => {
      // Add operational class if not already present
      if (!indicator.classList.contains('warning') && 
          !indicator.classList.contains('error') && 
          !indicator.classList.contains('inactive')) {
          indicator.classList.add('operational');
      }
  });
}

/**
* Responsive System Management
*/
function initResponsiveSystem() {
  // Handle responsive breakpoint changes
  const mediaQueries = {
      mobile: window.matchMedia('(max-width: 767px)'),
      tablet: window.matchMedia('(max-width: 991px)'),
      desktop: window.matchMedia('(min-width: 992px)')
  };
  
  // Listen for breakpoint changes
  Object.keys(mediaQueries).forEach(breakpoint => {
      const mq = mediaQueries[breakpoint];
      mq.addListener(() => handleBreakpointChange(breakpoint, mq.matches));
      handleBreakpointChange(breakpoint, mq.matches);
  });
}

/**
* Handle responsive breakpoint changes
*/
function handleBreakpointChange(breakpoint, matches) {
  document.body.classList.toggle(`aura-${breakpoint}`, matches);
  
  if (breakpoint === 'mobile' && matches) {
      // Optimize for mobile
      optimizeForMobile();
  }
}

/**
* Mobile optimizations
*/
function optimizeForMobile() {
  // Reduce animation intensity on mobile
  if (AURA.settings.reducedMotion) {
      document.body.classList.add('reduced-motion');
  }
  
  // Optimize touch interactions
  const touchElements = document.querySelectorAll('.btn, .nav-link, .card');
  touchElements.forEach(element => {
      element.style.cursor = 'pointer';
  });
}

/**
* Accessibility Enhancements
*/
function initAccessibility() {
  // Handle keyboard navigation
  document.addEventListener('keydown', handleKeyboardNavigation);
  
  // Handle focus management
  initFocusManagement();
  
  // Add ARIA labels where needed
  enhanceARIA();
}

/**
* Keyboard navigation handler
*/
function handleKeyboardNavigation(event) {
  // ESC key handling
  if (event.key === 'Escape') {
      closeModals();
      closeMobileMenu();
  }
  
  // Tab navigation enhancement
  if (event.key === 'Tab') {
      document.body.classList.add('keyboard-navigation');
  }
}

/**
* Focus management
*/
function initFocusManagement() {
  // Remove keyboard navigation class on mouse interaction
  document.addEventListener('mousedown', () => {
      document.body.classList.remove('keyboard-navigation');
  });
  
  // Enhanced focus indicators
  const focusableElements = document.querySelectorAll('a, button, input, select, textarea, [tabindex]');
  
  focusableElements.forEach(element => {
      element.addEventListener('focus', function() {
          this.classList.add('aura-focused');
      });
      
      element.addEventListener('blur', function() {
          this.classList.remove('aura-focused');
      });
  });
}

/**
* Enhance ARIA labels and accessibility
*/
function enhanceARIA() {
  // Add ARIA labels to status indicators
  const statusIndicators = document.querySelectorAll('.status-indicator');
  statusIndicators.forEach((indicator, index) => {
      if (!indicator.hasAttribute('aria-label')) {
          const status = indicator.classList.contains('operational') ? 'Operational' : 'Unknown';
          indicator.setAttribute('aria-label', `System status: ${status}`);
      }
  });
  
  // Add ARIA labels to metric displays
  const metricDisplays = document.querySelectorAll('[data-metric]');
  metricDisplays.forEach(metric => {
      const metricType = metric.dataset.metric;
      const value = metric.textContent;
      metric.setAttribute('aria-label', `${metricType}: ${value}`);
  });
}

/**
* Utility Functions
*/

/**
* Close all open modals
*/
function closeModals() {
  const modals = document.querySelectorAll('.modal.show, .modal.active');
  modals.forEach(modal => {
      modal.classList.remove('show', 'active');
  });
}

/**
* Close mobile menu
*/
function closeMobileMenu() {
  const mobileMenu = document.querySelector('.nav-menu');
  const toggleButton = document.querySelector('.mobile-menu-toggle');
  
  if (mobileMenu && mobileMenu.classList.contains('active')) {
      mobileMenu.classList.remove('active');
      if (toggleButton) {
          toggleButton.classList.remove('active');
      }
  }
}

/**
* Smooth scroll to element
*/
function smoothScrollTo(target, offset = 80) {
  const element = typeof target === 'string' ? document.querySelector(target) : target;
  
  if (element) {
      const targetPosition = element.getBoundingClientRect().top + window.pageYOffset - offset;
      
      window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
      });
  }
}

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
* Check if element is in viewport
*/
function isInViewport(element, threshold = 0) {
  const rect = element.getBoundingClientRect();
  const windowHeight = window.innerHeight || document.documentElement.clientHeight;
  const windowWidth = window.innerWidth || document.documentElement.clientWidth;
  
  return (
      rect.top >= -threshold &&
      rect.left >= -threshold &&
      rect.bottom <= windowHeight + threshold &&
      rect.right <= windowWidth + threshold
  );
}

/**
* Format numbers with appropriate suffixes
*/
function formatNumber(num) {
  if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
  } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
}

/**
* Generate random system ID
*/
function generateSystemID(prefix = 'SYS', length = 8) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let result = prefix + '-';
  for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

/**
* AURA Loading Sequence
* Three-phase loading animation
*/
function initLoadingSequence() {
  const loadingScreen = document.getElementById('loadingScreen');
  const loadingContainer = document.getElementById('loadingContainer');
  const welcomeScreen = document.getElementById('welcomeScreen');
  
  if (!loadingScreen) return;
  
  // Show loading screen
  loadingScreen.style.display = 'flex';
  
  // Phase 1: Logo and progress (0-4.5s)
  setTimeout(() => {
      const logo = loadingScreen.querySelector('.aura-logo');
      const subtitle = loadingScreen.querySelector('.aura-subtitle');
      const progressBar = loadingScreen.querySelector('.progress-bar');
      const loadingText = loadingScreen.querySelector('.loading-text');
      
      if (logo) {
          logo.style.opacity = '1';
          logo.style.animation = 'logoFadeIn 2s ease-out forwards';
      }
      
      if (subtitle) {
          setTimeout(() => {
              subtitle.style.opacity = '1';
              subtitle.style.animation = 'subtitleFadeIn 2s ease-out forwards';
          }, 1000);
      }
      
      if (progressBar) {
          setTimeout(() => {
              progressBar.style.animation = 'progressLoad 3s ease-out forwards';
          }, 2000);
      }
      
      if (loadingText) {
          setTimeout(() => {
              loadingText.style.opacity = '1';
              loadingText.style.animation = 'textFadeIn 1s ease-out forwards';
          }, 2500);
      }
  }, 500);
  
  // Phase 2: Welcome screen (4.5s-7s)
  setTimeout(() => {
      if (loadingContainer) {
          loadingContainer.style.opacity = '0';
      }
      
      setTimeout(() => {
          if (welcomeScreen) {
              welcomeScreen.classList.add('active');
          }
      }, 500);
  }, 4500);
  
  // Phase 3: Fade to main interface (7s+)
  setTimeout(() => {
      if (welcomeScreen) {
          welcomeScreen.style.opacity = '0';
      }
      
      setTimeout(() => {
          loadingScreen.classList.add('fade-out');
          
          setTimeout(() => {
              loadingScreen.style.display = 'none';
              document.body.style.overflow = 'auto';
              
              // Initialize main interface
              const mainInterface = document.getElementById('mainContent');
              if (mainInterface) {
                  mainInterface.style.opacity = '1';
                  mainInterface.style.transform = 'scale(1)';
              }
              
              AURA.loadingComplete = true;
          }, 1000);
      }, 800);
  }, 7000);
}

/**
* Export AURA functions for global access
*/
window.AURA = AURA;
window.initAURASystem = initAURASystem;
window.initLoadingSequence = initLoadingSequence;
window.smoothScrollTo = smoothScrollTo;
window.debounce = debounce;
window.throttle = throttle;
window.isInViewport = isInViewport;
window.formatNumber = formatNumber;
window.generateSystemID = generateSystemID;

// Auto-initialize if DOM is already loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAURASystem);
} else {
  initAURASystem();
}