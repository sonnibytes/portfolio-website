/**
 * AURA DataLogs Interface JavaScript
 * Advanced User Repository & Archive - Blog/DataLogs System
 * Version: 1.0.0
 */

// DataLogs System State
const DataLogsSystem = {
  initialized: false,
  currentView: 'grid',
  searchTimeout: null,
  animationSpeed: 300
};

/**
* Initialize DataLogs Interface
*/
function initDataLogsInterface() {
  console.log('🔍 DataLogs System Initializing...');
  
  // Initialize core components
  initCategoryHexagons();
  initSearchTerminal();
  initViewToggle();
  initSortControls();
  initDataLogCards();
  initScrollAnimations();
  
  // Mark as initialized
  DataLogsSystem.initialized = true;
  console.log('✅ DataLogs System Online');
}

/**
* Initialize Category Hexagon Navigation
*/
function initCategoryHexagons() {
  const hexagons = document.querySelectorAll('.category-hexagon');
  
  hexagons.forEach((hex, index) => {
      // Staggered animation on load
      hex.style.opacity = '0';
      hex.style.transform = 'translateY(20px)';
      
      setTimeout(() => {
          hex.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
          hex.style.opacity = '1';
          hex.style.transform = 'translateY(0)';
      }, index * 100);
      
      // Enhanced hover effects
      hex.addEventListener('mouseenter', function() {
          this.style.transform = 'translateY(-5px) scale(1.05)';
          
          // Add glow effect
          const color = this.style.getPropertyValue('--category-color') || '#b39ddb';
          this.style.boxShadow = `0 10px 30px ${color}40`;
      });
      
      hex.addEventListener('mouseleave', function() {
          this.style.transform = 'translateY(0) scale(1)';
          this.style.boxShadow = 'none';
      });
      
      // Keyboard navigation
      hex.addEventListener('keydown', function(e) {
          if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              this.click();
          }
      });
  });
}

/**
* Initialize Search Terminal
*/
function initSearchTerminal() {
  const searchInput = document.querySelector('.search-input');
  const searchForm = document.querySelector('.search-terminal');
  const searchContainer = document.querySelector('.search-container');
  
  if (!searchInput) return;
  
  // Terminal-style typing effect
  searchInput.addEventListener('input', function() {
      clearTimeout(DataLogsSystem.searchTimeout);
      
      // Add scanning line effect while typing
      searchContainer.classList.add('scanning-horizontal');
      
      DataLogsSystem.searchTimeout = setTimeout(() => {
          searchContainer.classList.remove('scanning-horizontal');
      }, 1000);
  });
  
  // Enhanced focus effects
  searchInput.addEventListener('focus', function() {
      searchContainer.classList.add('terminal-active');
      this.parentElement.classList.add('scanning-horizontal');
  });
  
  searchInput.addEventListener('blur', function() {
      searchContainer.classList.remove('terminal-active');
      this.parentElement.classList.remove('scanning-horizontal');
  });
  
  // Live search functionality (optional)
  if (searchInput.dataset.liveSearch === 'true') {
      searchInput.addEventListener('input', debounce(function() {
          performLiveSearch(this.value);
      }, 500));
  }
  
  // Terminal command simulation
  searchForm.addEventListener('submit', function(e) {
      const submitBtn = this.querySelector('.search-execute');
      
      // Add loading effect
      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
      submitBtn.style.pointerEvents = 'none';
      
      // Simulate processing delay for UX
      setTimeout(() => {
          // Form will submit normally
      }, 300);
  });
}

/**
* Initialize View Toggle Controls
*/
function initViewToggle() {
  const viewButtons = document.querySelectorAll('.view-btn');
  const contentGrid = document.querySelector('.datalogs-content-grid');
  
  viewButtons.forEach(btn => {
      btn.addEventListener('click', function() {
          // Update active state
          viewButtons.forEach(b => b.classList.remove('active'));
          this.classList.add('active');
          
          // Update view mode
          const viewMode = this.dataset.view;
          DataLogsSystem.currentView = viewMode;
          
          if (contentGrid) {
              // Add transition class
              contentGrid.style.transition = 'all 0.3s ease-out';
              contentGrid.className = `datalogs-content-grid ${viewMode}-view`;
              
              // Animate cards for new layout
              animateCardsForView(viewMode);
          }
          
          // Store preference
          localStorage.setItem('datalogViewMode', viewMode);
      });
  });
  
  // Restore saved view preference
  const savedView = localStorage.getItem('datalogViewMode');
  if (savedView) {
      const targetBtn = document.querySelector(`[data-view="${savedView}"]`);
      if (targetBtn) {
          targetBtn.click();
      }
  }
}

/**
* Initialize Sort Controls
*/
function initSortControls() {
  const sortSelect = document.getElementById('sortSelect');
  
  if (!sortSelect) return;
  
  sortSelect.addEventListener('change', function() {
      const sortValue = this.value;
      const url = new URL(window.location);
      
      // Update URL parameters
      url.searchParams.set('sort', sortValue);
      
      // Add loading effect
      this.style.opacity = '0.6';
      this.style.pointerEvents = 'none';
      
      // Navigate to sorted URL
      window.location.href = url.toString();
  });
  
  // Set current sort value from URL
  const urlParams = new URLSearchParams(window.location.search);
  const currentSort = urlParams.get('sort');
  if (currentSort && sortSelect.querySelector(`option[value="${currentSort}"]`)) {
      sortSelect.value = currentSort;
  }
}

/**
* Initialize DataLog Card Interactions
*/
function initDataLogCards() {
  const cards = document.querySelectorAll('.datalog-entry-card');
  
  cards.forEach((card, index) => {
      // Staggered entrance animation
      card.style.opacity = '0';
      card.style.transform = 'translateY(30px)';
      
      setTimeout(() => {
          card.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
          card.style.opacity = '1';
          card.style.transform = 'translateY(0)';
      }, index * 100 + 200);
      
      // Enhanced hover effects
      card.addEventListener('mouseenter', function() {
          this.style.transform = 'translateY(-8px) scale(1.02)';
          
          // Add subtle glow
          this.style.boxShadow = `
              0 15px 40px rgba(0, 0, 0, 0.4),
              0 0 20px rgba(179, 157, 219, 0.2)
          `;
      });
      
      card.addEventListener('mouseleave', function() {
          this.style.transform = 'translateY(0) scale(1)';
          this.style.boxShadow = '';
      });
      
      // Click to navigate (for mobile)
      card.addEventListener('click', function(e) {
          // Only if not clicking on a link
          if (!e.target.closest('a')) {
              const link = this.querySelector('.datalog-link');
              if (link) {
                  window.location.href = link.href;
              }
          }
      });
  });
}

/**
* Initialize Scroll-Based Animations
*/
function initScrollAnimations() {
  const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
  };
  
  const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
          if (entry.isIntersecting) {
              entry.target.classList.add('animate-in');
              
              // Special handling for different elements
              if (entry.target.classList.contains('datalog-entry-card')) {
                  animateDataLogCard(entry.target);
              }
              
              observer.unobserve(entry.target);
          }
      });
  }, observerOptions);
  
  // Observe cards that haven't been animated yet
  const cards = document.querySelectorAll('.datalog-entry-card:not(.animate-in)');
  cards.forEach(card => observer.observe(card));
}

/**
* Animate cards for view mode change
*/
function animateCardsForView(viewMode) {
  const cards = document.querySelectorAll('.datalog-entry-card');
  
  cards.forEach((card, index) => {
      // Fade out briefly
      card.style.opacity = '0.7';
      card.style.transform = 'scale(0.95)';
      
      setTimeout(() => {
          // Fade back in with new layout
          card.style.transition = 'all 0.3s ease-out';
          card.style.opacity = '1';
          card.style.transform = 'scale(1)';
          
          // Apply view-specific styling
          if (viewMode === 'list') {
              card.style.flexDirection = 'row';
          } else {
              card.style.flexDirection = 'column';
          }
      }, index * 50);
  });
}

/**
* Animate individual DataLog card
*/
function animateDataLogCard(card) {
  card.style.transform = 'translateY(0) scale(1)';
  card.style.opacity = '1';
  
  // Add scanning line effect
  card.classList.add('scanning-horizontal');
  
  setTimeout(() => {
      card.classList.remove('scanning-horizontal');
  }, 1000);
}

/**
* Perform live search (if enabled)
*/
function performLiveSearch(query) {
  if (!query.trim()) {
      showAllCards();
      return;
  }
  
  const cards = document.querySelectorAll('.datalog-entry-card');
  const searchTerms = query.toLowerCase().split(' ');
  
  cards.forEach(card => {
      const title = card.querySelector('.datalog-title')?.textContent.toLowerCase() || '';
      const excerpt = card.querySelector('.datalog-excerpt')?.textContent.toLowerCase() || '';
      const category = card.querySelector('.datalog-category-info')?.textContent.toLowerCase() || '';
      
      const content = `${title} ${excerpt} ${category}`;
      const matches = searchTerms.every(term => content.includes(term));
      
      if (matches) {
          card.style.display = 'flex';
          card.style.opacity = '1';
          card.style.transform = 'translateY(0)';
      } else {
          card.style.opacity = '0.3';
          card.style.transform = 'translateY(-10px)';
          setTimeout(() => {
              if (card.style.opacity === '0.3') {
                  card.style.display = 'none';
              }
          }, 300);
      }
  });
  
  // Update results count
  updateSearchResultsCount();
}

/**
* Show all cards (clear search)
*/
function showAllCards() {
  const cards = document.querySelectorAll('.datalog-entry-card');
  
  cards.forEach((card, index) => {
      card.style.display = 'flex';
      
      setTimeout(() => {
          card.style.opacity = '1';
          card.style.transform = 'translateY(0)';
      }, index * 50);
  });
}

/**
* Update search results count
*/
function updateSearchResultsCount() {
  const visibleCards = document.querySelectorAll('.datalog-entry-card:not([style*="display: none"])');
  const totalCards = document.querySelectorAll('.datalog-entry-card');
  
  // Update or create results indicator
  let resultsIndicator = document.querySelector('.search-results-count');
  
  if (!resultsIndicator) {
      resultsIndicator = document.createElement('div');
      resultsIndicator.className = 'search-results-count';
      resultsIndicator.style.cssText = `
          font-family: var(--font-code);
          font-size: 0.8rem;
          color: var(--color-text-tertiary);
          text-align: center;
          margin-top: var(--spacing-md);
          padding: var(--spacing-xs);
          background: rgba(179, 157, 219, 0.05);
          border-radius: var(--border-radius-sm);
      `;
      
      const controlsPanel = document.querySelector('.datalogs-controls');
      if (controlsPanel) {
          controlsPanel.appendChild(resultsIndicator);
      }
  }
  
  resultsIndicator.textContent = `Showing ${visibleCards.length} of ${totalCards.length} datalogs`;
  
  if (visibleCards.length === 0) {
      resultsIndicator.textContent = 'No datalogs found matching your search';
      resultsIndicator.style.color = 'var(--color-coral)';
  } else {
      resultsIndicator.style.color = 'var(--color-text-tertiary)';
  }
}

/**
* Initialize Table of Contents (for detail pages)
*/
function initTableOfContents() {
  const tocLinks = document.querySelectorAll('.toc-link');
  const headings = document.querySelectorAll('.datalog-content h2, .datalog-content h3, .datalog-content h4');
  
  if (tocLinks.length === 0 || headings.length === 0) return;
  
  // Smooth scroll for TOC links
  tocLinks.forEach(link => {
      link.addEventListener('click', function(e) {
          e.preventDefault();
          
          const targetId = this.getAttribute('href').substring(1);
          const targetElement = document.getElementById(targetId);
          
          if (targetElement) {
              smoothScrollTo(targetElement, 100);
              
              // Add highlight effect
              targetElement.style.color = 'var(--color-lavender)';
              setTimeout(() => {
                  targetElement.style.color = '';
              }, 2000);
          }
      });
  });
  
  // Highlight current section in TOC
  const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
          const id = entry.target.id;
          const tocLink = document.querySelector(`.toc-link[href="#${id}"]`);
          
          if (tocLink) {
              if (entry.isIntersecting) {
                  tocLinks.forEach(link => link.classList.remove('active'));
                  tocLink.classList.add('active');
              }
          }
      });
  }, {
      threshold: 0.5,
      rootMargin: '-100px 0px -50% 0px'
  });
  
  headings.forEach(heading => {
      if (heading.id) {
          observer.observe(heading);
      }
  });
}

/**
* Initialize Featured DataLog Effects
*/
function initFeaturedDataLog() {
  const featuredCard = document.querySelector('.featured-datalog');
  
  if (!featuredCard) return;
  
  // Enhanced featured card effects
  featuredCard.style.position = 'relative';
  featuredCard.style.overflow = 'hidden';
  
  // Add animated border
  const animatedBorder = document.createElement('div');
  animatedBorder.style.cssText = `
      position: absolute;
      top: -2px;
      left: -2px;
      right: -2px;
      bottom: -2px;
      background: linear-gradient(45deg, var(--color-lavender), var(--color-coral), var(--color-teal));
      z-index: -1;
      border-radius: var(--border-radius-xl);
      opacity: 0.6;
      animation: borderGlow 3s ease-in-out infinite alternate;
  `;
  
  featuredCard.appendChild(animatedBorder);
  
  // Add glow animation keyframes
  if (!document.querySelector('#borderGlowKeyframes')) {
      const style = document.createElement('style');
      style.id = 'borderGlowKeyframes';
      style.textContent = `
          @keyframes borderGlow {
              0% { opacity: 0.6; transform: scale(1); }
              100% { opacity: 0.8; transform: scale(1.02); }
          }
      `;
      document.head.appendChild(style);
  }
}

/**
* Initialize Category Filter (for sidebar)
*/
function initCategoryFilter() {
  const filterItems = document.querySelectorAll('.filter-item');
  
  filterItems.forEach(item => {
      item.addEventListener('click', function(e) {
          e.preventDefault();
          
          // Update active state
          filterItems.forEach(f => f.classList.remove('active'));
          this.classList.add('active');
          
          // Add loading effect
          this.style.opacity = '0.6';
          
          // Navigate to filtered URL
          setTimeout(() => {
              window.location.href = this.href;
          }, 200);
      });
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
* Initialize Keyboard Shortcuts
*/
function initKeyboardShortcuts() {
  document.addEventListener('keydown', function(e) {
      // Only activate if not in an input field
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
          return;
      }
      
      switch(e.key) {
          case '/':
              e.preventDefault();
              const searchInput = document.querySelector('.search-input');
              if (searchInput) {
                  searchInput.focus();
              }
              break;
              
          case 'g':
              if (e.shiftKey) { // Shift + G
                  e.preventDefault();
                  const gridViewBtn = document.querySelector('[data-view="grid"]');
                  if (gridViewBtn) gridViewBtn.click();
              }
              break;
              
          case 'l':
              if (e.shiftKey) { // Shift + L
                  e.preventDefault();
                  const listViewBtn = document.querySelector('[data-view="list"]');
                  if (listViewBtn) listViewBtn.click();
              }
              break;
              
          case 'Escape':
              // Clear search
              const searchInput = document.querySelector('.search-input');
              if (searchInput && searchInput.value) {
                  searchInput.value = '';
                  searchInput.dispatchEvent(new Event('input'));
                  searchInput.blur();
              }
              break;
      }
  });
}

/**
* Initialize Pagination Enhancement
*/
function initPaginationEnhancement() {
  const paginationLinks = document.querySelectorAll('.pagination-link');
  
  paginationLinks.forEach(link => {
      if (!link.classList.contains('disabled')) {
          link.addEventListener('click', function(e) {
              // Add loading effect
              this.style.opacity = '0.6';
              this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
              
              // Let the link navigate normally
              // The loading effect will be visible until the new page loads
          });
      }
  });
}

/**
* Initialize DataLog Metrics (for admin/dashboard views)
*/
function initDataLogMetrics() {
  const metricElements = document.querySelectorAll('[data-metric]');
  
  metricElements.forEach(element => {
      const metricType = element.dataset.metric;
      
      // Simulate real-time metric updates for demo purposes
      if (metricType === 'total_logs') {
          // Animate counter
          animateCounter(element, parseInt(element.textContent) || 0);
      }
  });
}

/**
* Animate number counter
*/
function animateCounter(element, target) {
  const duration = 2000;
  const start = 0;
  const increment = target / (duration / 16);
  let current = start;
  
  const updateCounter = () => {
      current += increment;
      if (current < target) {
          element.textContent = Math.floor(current);
          requestAnimationFrame(updateCounter);
      } else {
          element.textContent = target;
      }
  };
  
  requestAnimationFrame(updateCounter);
}

/**
* Debounce function for search
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
* Smooth scroll utility
*/
function smoothScrollTo(target, offset = 80) {
  const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
  
  window.scrollTo({
      top: targetPosition,
      behavior: 'smooth'
  });
}

/**
* Initialize on DOM ready
*/
document.addEventListener('DOMContentLoaded', function() {
  // Initialize all DataLogs components
  initDataLogsInterface();
  initTableOfContents();
  initFeaturedDataLog();
  initCategoryFilter();
  initRealtimeClock();
  initKeyboardShortcuts();
  initPaginationEnhancement();
  initDataLogMetrics();
  
  // Add keyboard shortcut hints for power users
  console.log(`
🚀 DataLogs Keyboard Shortcuts:
 / - Focus search
 Shift+G - Grid view
 Shift+L - List view
 Esc - Clear search
  `);
});

/**
* Export functions for global access
*/
window.DataLogsSystem = DataLogsSystem;
window.initDataLogsInterface = initDataLogsInterface;
window.initTableOfContents = initTableOfContents;