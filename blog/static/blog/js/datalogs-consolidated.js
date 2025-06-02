/**
 * AURA DataLogs - Consolidated Master JavaScript
 * Advanced User Repository & Archive - Complete DataLogs Functionality
 * Version: 3.0.0 - Consolidated from all components and templates
 * 
 * This file contains ALL DataLogs JavaScript in organized modules:
 * - Glass hexagon navigation with smooth scrolling
 * - Enhanced search with real-time suggestions
 * - Filter panels and interactive controls
 * - Timeline animations and interactions
 * - Card hover effects and state management
 * - View toggles and sorting functionality
 * - Terminal code display enhancements
 * - Responsive behavior and touch support
 */

// ========== DATALOG INTERFACE CORE ========== //

class DatalogInterface {
    constructor() {
        this.isInitialized = false;
        this.components = {};
        this.state = {
            currentView: 'grid',
            searchQuery: '',
            activeFilters: {},
            currentCategory: null,
            isFilterPanelOpen: false,
            isSearchPanelOpen: false
        };
        
        // Configuration
        this.config = {
            animationDuration: 300,
            debounceDelay: 300,
            scrollDuration: 500,
            maxSearchSuggestions: 5,
            cardAnimationDelay: 100,
            enableDebugMode: false
        };
        
        // Bind methods
        this.init = this.init.bind(this);
        this.handleResize = this.handleResize.bind(this);
        this.handleKeyboardShortcuts = this.handleKeyboardShortcuts.bind(this);
    }
    
    // ========== INITIALIZATION ========== //
    
    init() {
        if (this.isInitialized) return;
        
        console.log('🚀 DataLogs interface initializing...');
        
        try {
            // Initialize components in order
            this.initializeHexagonNavigation();
            this.initializeEnhancedSearch();
            this.initializeFilterPanels();
            this.initializeGridControls();
            this.initializeCardInteractions();
            this.initializeTerminalDisplay();
            this.initializeTimelineComponents();
            this.initializeResponsiveBehavior();
            this.initializeKeyboardNavigation();
            this.initializeScrollEffects();
            this.initializePerformanceOptimizations();
            
            // Set up global event listeners
            this.setupGlobalEventListeners();
            
            // Load saved preferences
            this.loadUserPreferences();
            
            this.isInitialized = true;
            console.log('✅ DataLogs interface initialized successfully');
            
            // Dispatch custom event
            window.dispatchEvent(new CustomEvent('datalogsInitialized', {
                detail: { interface: this }
            }));
            
        } catch (error) {
            console.error('❌ DataLogs initialization failed:', error);
        }
    }
    
    // ========== GLASS HEXAGON NAVIGATION ========== //
    
    initializeHexagonNavigation() {
        const scrollContainer = document.getElementById('categoriesGrid');
        const leftBtn = document.getElementById('categoryScrollLeft');
        const rightBtn = document.getElementById('categoryScrollRight');
        
        if (!scrollContainer) return;
        
        console.log('🔷 Initializing hexagon navigation...');
        
        // Create navigation component
        this.components.hexagonNav = {
            container: scrollContainer,
            leftBtn: leftBtn,
            rightBtn: rightBtn,
            isScrolling: false,
            scrollPosition: 0
        };
        
        // Scroll functionality
        if (leftBtn && rightBtn) {
            leftBtn.addEventListener('click', () => this.scrollCategories('left'));
            rightBtn.addEventListener('click', () => this.scrollCategories('right'));
        }
        
        // Touch/swipe support
        this.initializeTouchNavigation(scrollContainer);
        
        // Scroll position tracking
        scrollContainer.addEventListener('scroll', 
            this.debounce(() => this.updateScrollButtons(), 100)
        );
        
        // Initial button state
        setTimeout(() => this.updateScrollButtons(), 100);
        
        // Resize handler
        window.addEventListener('resize', 
            this.debounce(() => this.updateScrollButtons(), 200)
        );
        
        // Enhanced hexagon interactions
        this.initializeHexagonInteractions();
        
        console.log('✅ Hexagon navigation initialized');
    }
    
    scrollCategories(direction) {
        const { container } = this.components.hexagonNav;
        if (!container || this.components.hexagonNav.isScrolling) return;
        
        this.components.hexagonNav.isScrolling = true;
        
        const scrollAmount = 200;
        const targetScroll = direction === 'left' 
            ? container.scrollLeft - scrollAmount 
            : container.scrollLeft + scrollAmount;
        
        // Smooth scroll with easing
        this.smoothScroll(container, targetScroll, this.config.scrollDuration)
            .then(() => {
                this.components.hexagonNav.isScrolling = false;
                this.updateScrollButtons();
            });
    }
    
    updateScrollButtons() {
        const nav = this.components.hexagonNav;
        if (!nav.container || !nav.leftBtn || !nav.rightBtn) return;
        
        const { scrollLeft, scrollWidth, clientWidth } = nav.container;
        
        // Update button states
        nav.leftBtn.disabled = scrollLeft <= 0;
        nav.rightBtn.disabled = scrollLeft >= scrollWidth - clientWidth - 1;
        
        // Visual feedback
        nav.leftBtn.style.opacity = nav.leftBtn.disabled ? '0.3' : '1';
        nav.rightBtn.style.opacity = nav.rightBtn.disabled ? '0.3' : '1';
        
        nav.leftBtn.style.transform = nav.leftBtn.disabled ? 'scale(0.9)' : 'scale(1)';
        nav.rightBtn.style.transform = nav.rightBtn.disabled ? 'scale(0.9)' : 'scale(1)';
    }
    
    initializeTouchNavigation(container) {
        let startX = 0;
        let scrollStart = 0;
        let isTouch = false;
        
        container.addEventListener('touchstart', (e) => {
            startX = e.touches[0].pageX;
            scrollStart = container.scrollLeft;
            isTouch = true;
        }, { passive: true });
        
        container.addEventListener('touchmove', (e) => {
            if (!isTouch) return;
            
            const x = e.touches[0].pageX;
            const walk = (startX - x) * 2; // Multiply for faster scroll
            container.scrollLeft = scrollStart + walk;
        }, { passive: true });
        
        container.addEventListener('touchend', () => {
            isTouch = false;
            this.updateScrollButtons();
        });
    }
    
    initializeHexagonInteractions() {
        const hexagonItems = document.querySelectorAll('.category-nav-item');
        
        hexagonItems.forEach((item, index) => {
            // Enhanced hover effects
            item.addEventListener('mouseenter', () => {
                this.animateHexagonHover(item, true);
            });
            
            item.addEventListener('mouseleave', () => {
                this.animateHexagonHover(item, false);
            });
            
            // Click ripple effect
            item.addEventListener('click', (e) => {
                this.createRippleEffect(item, e);
            });
            
            // Staggered entrance animation
            setTimeout(() => {
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }
    
    animateHexagonHover(item, isHover) {
        const hexagon = item.querySelector('.category-hexagon.glass-hex');
        const text = item.querySelector('.hex-text');
        
        if (!hexagon || !text) return;
        
        if (isHover) {
            hexagon.style.transform = 'scale(1.05)';
            text.style.transform = 'scale(1.05)';
            
            // Add scanning effect
            if (!item.classList.contains('scanning-hex')) {
                item.classList.add('scanning-hex');
                setTimeout(() => item.classList.remove('scanning-hex'), 1500);
            }
        } else {
            const baseScale = item.classList.contains('active') ? '1.1' : '1';
            hexagon.style.transform = `scale(${baseScale})`;
            text.style.transform = `scale(${baseScale})`;
        }
    }
    
    createRippleEffect(element, event) {
        const ripple = document.createElement('div');
        ripple.className = 'hex-ripple';
        
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
            background: rgba(179, 157, 219, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: hexRipple 0.6s ease-out;
            pointer-events: none;
            z-index: 5;
        `;
        
        element.style.position = 'relative';
        element.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }
    
    // ========== ENHANCED SEARCH SYSTEM ========== //
    
    initializeEnhancedSearch() {
        const searchInputs = document.querySelectorAll('.search-input-enhanced, .datalog-search-input');
        const searchSuggestions = document.getElementById('searchSuggestions');
        const searchToggle = document.getElementById('datalogsSearchToggle');
        const searchPanel = document.getElementById('datalogsSearchPanel');
        
        console.log('🔍 Initializing enhanced search...');
        
        // Create search component
        this.components.search = {
            inputs: searchInputs,
            suggestions: searchSuggestions,
            toggle: searchToggle,
            panel: searchPanel,
            currentQuery: '',
            suggestionCache: new Map(),
            isLoading: false
        };
        
        // Initialize search inputs
        searchInputs.forEach(input => {
            this.initializeSearchInput(input);
        });
        
        // Search panel toggle
        if (searchToggle && searchPanel) {
            searchToggle.addEventListener('click', () => this.toggleSearchPanel());
        }
        
        // Enhanced keyboard navigation in suggestions
        if (searchSuggestions) {
            this.initializeSearchKeyboardNav(searchSuggestions);
        }
        
        // Global search shortcut (Ctrl/Cmd + K)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.focusSearch();
            }
        });
        
        console.log('✅ Enhanced search initialized');
    }
    
    initializeSearchInput(input) {
        let searchTimeout;
        
        // Real-time search with debouncing
        input.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();
            
            this.components.search.currentQuery = query;
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    this.loadSearchSuggestions(query);
                }, this.config.debounceDelay);
            } else {
                this.hideSearchSuggestions();
            }
        });
        
        // Enhanced focus behavior
        input.addEventListener('focus', () => {
            const query = input.value.trim();
            if (query.length >= 2) {
                this.loadSearchSuggestions(query);
            }
            
            // Add search focus effect
            input.closest('.search-input-wrapper')?.classList.add('search-focused');
        });
        
        input.addEventListener('blur', () => {
            // Delay hiding to allow for suggestion clicks
            setTimeout(() => {
                this.hideSearchSuggestions();
                input.closest('.search-input-wrapper')?.classList.remove('search-focused');
            }, 200);
        });
        
        // Enhanced keyboard navigation
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideSearchSuggestions();
                input.blur();
            } else if (e.key === 'Enter' && !this.hasActiveSuggestion()) {
                // Submit search if no suggestion is selected
                this.submitSearch(input.value);
            }
        });
    }
    
    loadSearchSuggestions(query) {
        const { suggestions, suggestionCache } = this.components.search;
        if (!suggestions) return;
        
        // Check cache first
        if (suggestionCache.has(query)) {
            this.displaySearchSuggestions(suggestionCache.get(query));
            return;
        }
        
        // Show loading state
        this.showSearchLoading();
        
        // Simulate API call with enhanced suggestions
        setTimeout(() => {
            const suggestionsData = this.generateSearchSuggestions(query);
            suggestionCache.set(query, suggestionsData);
            this.displaySearchSuggestions(suggestionsData);
        }, 200);
    }
    
    generateSearchSuggestions(query) {
        const suggestions = [
            { text: 'Machine Learning Fundamentals', type: 'post', icon: 'fas fa-brain', url: '#' },
            { text: 'Python Data Analysis', type: 'post', icon: 'fas fa-chart-line', url: '#' },
            { text: 'Django Best Practices', type: 'post', icon: 'fas fa-code', url: '#' },
            { text: 'API Development', type: 'category', icon: 'fas fa-plug', url: '#' },
            { text: 'Database Optimization', type: 'post', icon: 'fas fa-database', url: '#' },
            { text: 'Neural Networks', type: 'tag', icon: 'fas fa-tag', url: '#' },
            { text: 'System Architecture', type: 'post', icon: 'fas fa-sitemap', url: '#' },
            { text: 'Algorithms & Data Structures', type: 'post', icon: 'fas fa-project-diagram', url: '#' }
        ];
        
        return suggestions
            .filter(s => s.text.toLowerCase().includes(query.toLowerCase()))
            .slice(0, this.config.maxSearchSuggestions);
    }
    
    showSearchLoading() {
        const { suggestions } = this.components.search;
        if (!suggestions) return;
        
        const suggestionsContent = suggestions.querySelector('#suggestionsContent') || 
                                 suggestions.querySelector('.suggestions-content');
        
        if (suggestionsContent) {
            suggestionsContent.innerHTML = `
                <div class="suggestions-loading">
                    <span>Searching...</span>
                </div>
            `;
        }
        
        this.showSearchSuggestions();
    }
    
    displaySearchSuggestions(suggestionsData) {
        const { suggestions } = this.components.search;
        if (!suggestions) return;
        
        const suggestionsContent = suggestions.querySelector('#suggestionsContent') || 
                                 suggestions.querySelector('.suggestions-content');
        
        if (!suggestionsContent) return;
        
        if (suggestionsData.length === 0) {
            suggestionsContent.innerHTML = `
                <div class="search-suggestion-item no-results">
                    <i class="fas fa-info-circle"></i>
                    <span class="suggestion-text">No suggestions found</span>
                </div>
            `;
        } else {
            const suggestionsHTML = suggestionsData.map((suggestion, index) => `
                <div class="search-suggestion-item" 
                     data-index="${index}"
                     onclick="datalogInterface.selectSuggestion('${suggestion.text}', '${suggestion.url}')">
                    <i class="${suggestion.icon}"></i>
                    <span class="suggestion-text">${suggestion.text}</span>
                    <span class="suggestion-type">${suggestion.type}</span>
                </div>
            `).join('');
            
            suggestionsContent.innerHTML = suggestionsHTML;
        }
        
        this.showSearchSuggestions();
    }
    
    showSearchSuggestions() {
        const { suggestions } = this.components.search;
        if (!suggestions) return;
        
        suggestions.style.display = 'block';
        // Force reflow
        suggestions.offsetHeight;
        suggestions.classList.add('show');
    }
    
    hideSearchSuggestions() {
        const { suggestions } = this.components.search;
        if (!suggestions) return;
        
        suggestions.classList.remove('show');
        setTimeout(() => {
            suggestions.style.display = 'none';
        }, 200);
    }
    
    selectSuggestion(suggestionText, url) {
        const { inputs } = this.components.search;
        
        inputs.forEach(input => {
            input.value = suggestionText;
        });
        
        this.hideSearchSuggestions();
        
        if (url && url !== '#') {
            window.location.href = url;
        } else {
            this.submitSearch(suggestionText);
        }
    }
    
    submitSearch(query) {
        if (!query.trim()) return;
        
        // Build search URL
        const searchUrl = new URL(window.location.origin + '/blog/search/');
        searchUrl.searchParams.set('q', query.trim());
        
        // Navigate to search results
        window.location.href = searchUrl.toString();
    }
    
    toggleSearchPanel() {
        const { panel, toggle } = this.components.search;
        if (!panel || !toggle) return;
        
        const isOpen = this.state.isSearchPanelOpen;
        
        if (isOpen) {
            panel.classList.remove('show');
            toggle.classList.remove('active');
            this.state.isSearchPanelOpen = false;
        } else {
            panel.classList.add('show');
            toggle.classList.add('active');
            this.state.isSearchPanelOpen = true;
            
            // Focus search input
            const searchInput = panel.querySelector('.datalog-search-input');
            if (searchInput) {
                setTimeout(() => searchInput.focus(), 100);
            }
            
            // Close filter panel if open
            this.closeFilterPanel();
        }
    }
    
    focusSearch() {
        const searchInput = document.querySelector('.search-input-enhanced, .datalog-search-input');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        } else {
            // Open search panel if no visible input
            this.toggleSearchPanel();
        }
    }
    
    // ========== FILTER PANELS ========== //
    
    initializeFilterPanels() {
        const filterToggle = document.getElementById('datalogsFilterToggle');
        const filterPanel = document.getElementById('datalogsFilterPanel');
        const closeFilters = document.getElementById('closeFilters');
        const clearFilters = document.getElementById('clearFilters');
        
        console.log('🎛️ Initializing filter panels...');
        
        // Create filter component
        this.components.filters = {
            toggle: filterToggle,
            panel: filterPanel,
            closeBtn: closeFilters,
            clearBtn: clearFilters,
            form: document.getElementById('datalogsFilterForm')
        };
        
        // Filter toggle
        if (filterToggle && filterPanel) {
            filterToggle.addEventListener('click', () => this.toggleFilterPanel());
        }
        
        // Close filter panel
        if (closeFilters) {
            closeFilters.addEventListener('click', () => this.closeFilterPanel());
        }
        
        // Clear filters
        if (clearFilters) {
            clearFilters.addEventListener('click', () => this.clearAllFilters());
        }
        
        // Initialize individual filters
        this.initializeTagFilters();
        this.initializeDateRangeFilters();
        this.initializeQuickFilters();
        
        // Close panel when clicking outside
        document.addEventListener('click', (e) => {
            if (filterPanel && 
                this.state.isFilterPanelOpen && 
                !filterPanel.contains(e.target) && 
                !filterToggle?.contains(e.target)) {
                this.closeFilterPanel();
            }
        });
        
        console.log('✅ Filter panels initialized');
    }
    
    toggleFilterPanel() {
        const { panel, toggle } = this.components.filters;
        if (!panel || !toggle) return;
        
        const isOpen = this.state.isFilterPanelOpen;
        
        if (isOpen) {
            this.closeFilterPanel();
        } else {
            panel.style.display = 'block';
            // Force reflow
            panel.offsetHeight;
            panel.classList.add('show');
            toggle.classList.add('active');
            this.state.isFilterPanelOpen = true;
            
            // Close search panel if open
            if (this.state.isSearchPanelOpen) {
                this.toggleSearchPanel();
            }
        }
    }
    
    closeFilterPanel() {
        const { panel, toggle } = this.components.filters;
        if (!panel || !toggle) return;
        
        panel.classList.remove('show');
        toggle.classList.remove('active');
        this.state.isFilterPanelOpen = false;
        
        setTimeout(() => {
            panel.style.display = 'none';
        }, this.config.animationDuration);
    }
    
    clearAllFilters() {
        const { form } = this.components.filters;
        if (!form) return;
        
        // Reset form
        form.reset();
        
        // Clear state
        this.state.activeFilters = {};
        
        // Redirect to clean URL
        const cleanUrl = new URL(window.location);
        const keysToRemove = ['category', 'tag', 'date_from', 'date_to', 'reading_time', 'featured', 'has_code'];
        
        keysToRemove.forEach(key => {
            cleanUrl.searchParams.delete(key);
        });
        
        window.location.href = cleanUrl.toString();
    }
    
    initializeTagFilters() {
        const tagSearch = document.getElementById('tagSearch');
        const tagOptions = document.querySelectorAll('.tag-option');
        
        if (!tagSearch || tagOptions.length === 0) return;
        
        tagSearch.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            
            tagOptions.forEach(option => {
                const tagName = option.dataset.tag || 
                               option.querySelector('.tag-badge')?.textContent.toLowerCase();
                
                if (tagName && tagName.includes(searchTerm)) {
                    option.style.display = 'flex';
                } else {
                    option.style.display = 'none';
                }
            });
        });
    }
    
    initializeDateRangeFilters() {
        const dateFrom = document.querySelector('input[name="date_from"]');
        const dateTo = document.querySelector('input[name="date_to"]');
        
        if (!dateFrom || !dateTo) return;
        
        // Date validation
        dateFrom.addEventListener('change', () => {
            if (dateTo.value && dateFrom.value > dateTo.value) {
                dateTo.value = dateFrom.value;
            }
        });
        
        dateTo.addEventListener('change', () => {
            if (dateFrom.value && dateTo.value < dateFrom.value) {
                dateFrom.value = dateTo.value;
            }
        });
    }
    
    initializeQuickFilters() {
        const quickFilters = document.querySelectorAll('.filter-tag, .filter-chip');
        
        quickFilters.forEach(filter => {
            filter.addEventListener('click', (e) => {
                // Add visual feedback
                filter.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    filter.style.transform = '';
                }, 150);
                
                // Track filter usage
                const filterType = filter.textContent.trim();
                console.log('Filter clicked:', filterType);
            });
        });
    }
    
    // ========== GRID CONTROLS ========== //
    
    initializeGridControls() {
        const viewToggleButtons = document.querySelectorAll('.view-toggle-btn, .view-btn');
        const sortSelects = document.querySelectorAll('#datalogsSort, #categorySort, #archiveSort');
        
        console.log('📊 Initializing grid controls...');
        
        // View toggles
        viewToggleButtons.forEach(btn => {
            btn.addEventListener('click', () => this.handleViewToggle(btn));
        });
        
        // Sort controls
        sortSelects.forEach(select => {
            select.addEventListener('change', (e) => this.handleSortChange(e.target));
        });
        
        // Restore saved view preference
        this.restoreViewPreference();
        
        console.log('✅ Grid controls initialized');
    }
    
    handleViewToggle(button) {
        const viewType = button.dataset.view;
        if (!viewType) return;
        
        // Update button states
        document.querySelectorAll('.view-toggle-btn, .view-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');
        
        // Update grid/content layout
        this.updateContentView(viewType);
        
        // Save preference
        localStorage.setItem('datalogsViewMode', viewType);
        this.state.currentView = viewType;
    }
    
    updateContentView(viewType) {
        const gridContainers = document.querySelectorAll(
            '.datalogs-grid, .datalogs-main-content, #datalogsGrid, .category-posts-grid, #searchResultsGrid'
        );
        
        gridContainers.forEach(container => {
            if (!container) return;
            
            // Add loading state
            container.style.opacity = '0.7';
            container.style.pointerEvents = 'none';
            
            setTimeout(() => {
                // Update classes
                container.className = container.className.replace(/\b\w+-view\b/g, '');
                container.classList.add(`${viewType}-view`);
                
                // Restore normal state
                container.style.opacity = '1';
                container.style.pointerEvents = 'auto';
                
                // Re-animate cards
                this.animateCardsEntrance(container);
                
            }, 200);
        });
    }
    
    handleSortChange(selectElement) {
        const sortValue = selectElement.value;
        console.log('Sorting by:', sortValue);
        
        // Add loading state to content
        const container = selectElement.closest('.container') || 
                         document.querySelector('.datalogs-main-content');
        
        if (container) {
            container.style.opacity = '0.6';
            container.style.pointerEvents = 'none';
            
            // In a real app, this would trigger a reload or AJAX update
            setTimeout(() => {
                container.style.opacity = '1';
                container.style.pointerEvents = 'auto';
            }, 500);
        }
    }
    
    restoreViewPreference() {
        const savedView = localStorage.getItem('datalogsViewMode');
        if (savedView) {
            const targetBtn = document.querySelector(`[data-view="${savedView}"]`);
            if (targetBtn) {
                targetBtn.click();
            }
        }
    }
    
    // ========== CARD INTERACTIONS ========== //
    
    initializeCardInteractions() {
        console.log('🎴 Initializing card interactions...');
        
        // Initialize all card types
        this.initializeDatalogCards();
        this.initializeTimelineCards();
        this.initializeMetricCards();
        
        // Global card entrance animations
        this.animateCardsEntrance(document);
        
        console.log('✅ Card interactions initialized');
    }
    
    initializeDatalogCards() {
        const datalogCards = document.querySelectorAll('.datalog-card');
        
        datalogCards.forEach((card, index) => {
            // Enhanced hover effects
            card.addEventListener('mouseenter', () => {
                this.animateCardHover(card, true);
            });
            
            card.addEventListener('mouseleave', () => {
                this.animateCardHover(card, false);
            });
            
            // Click handling with ripple effect
            card.addEventListener('click', (e) => {
                if (e.target.closest('a, button')) return; // Don't interfere with links/buttons
                
                // Create ripple effect
                this.createCardRipple(card, e);
                
                // Navigate to post
                const link = card.querySelector('.datalog-title a, .read-more-btn');
                if (link) {
                    setTimeout(() => {
                        link.click();
                    }, 200);
                }
            });
            
            // Intersection observer for scroll animations
            this.observeCardEntrance(card, index);
        });
    }
    
    initializeTimelineCards() {
        const timelineCards = document.querySelectorAll('.timeline-post-card');
        
        timelineCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                // Enhanced timeline hover effects
                card.style.transform = 'translateX(10px) scale(1.02)';
                card.classList.add('scanning-horizontal');
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateX(0) scale(1)';
                card.classList.remove('scanning-horizontal');
            });
        });
    }
    
    initializeMetricCards() {
        const metricCards = document.querySelectorAll('.metric-item, .metric-card');
        
        metricCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-3px) scale(1.02)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) scale(1)';
            });
        });
    }
    
    animateCardHover(card, isHover) {
        if (isHover) {
            card.style.transform = 'translateY(-8px) scale(1.02)';
            
            // Add scanning line effect
            if (!card.querySelector('.card-scanning-line')) {
                const scanLine = document.createElement('div');
                scanLine.className = 'card-scanning-line';
                card.appendChild(scanLine);
                
                // Remove after animation
                setTimeout(() => scanLine.remove(), 1500);
            }
        } else {
            card.style.transform = 'translateY(0) scale(1)';
        }
    }
    
    createCardRipple(card, event) {
        const ripple = document.createElement('div');
        ripple.className = 'card-ripple';
        
        const rect = card.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(179, 157, 219, 0.2);
            border-radius: 50%;
            transform: scale(0);
            animation: cardRipple 0.6s ease-out;
            pointer-events: none;
            z-index: 5;
        `;
        
        card.style.position = 'relative';
        card.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }
    
    observeCardEntrance(card, index) {
        // Set initial state
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, index * this.config.cardAnimationDelay);
                    
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        observer.observe(card);
    }
    
    animateCardsEntrance(container) {
        const cards = container.querySelectorAll('.datalog-card, .timeline-post-card');
        
        cards.forEach((card, index) => {
            card.style.opacity = '0.7';
            card.style.transform = 'scale(0.95)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.3s ease';
                card.style.opacity = '1';
                card.style.transform = 'scale(1)';
            }, index * 50);
        });
    }
    
    // ========== TERMINAL DISPLAY ENHANCEMENTS ========== //
    
    initializeTerminalDisplay() {
        const terminals = document.querySelectorAll('.terminal-window, .featured-terminal-container');
        
        console.log('💻 Initializing terminal displays...');
        
        terminals.forEach(terminal => {
            this.enhanceTerminal(terminal);
        });
        
        // Copy button functionality
        this.initializeCopyButtons();
        
        console.log('✅ Terminal displays initialized');
    }
    
    enhanceTerminal(terminal) {
        // Add terminal activation effect
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.classList.add('terminal-active');
                        this.typewriterEffect(entry.target);
                    }, 300);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.3 });
        
        observer.observe(terminal);
        
        // Terminal button interactions
        const buttons = terminal.querySelectorAll('.terminal-button');
        buttons.forEach(button => {
            button.addEventListener('click', () => {
                button.style.transform = 'scale(0.8)';
                setTimeout(() => {
                    button.style.transform = 'scale(1)';
                }, 100);
            });
        });
    }
    
    typewriterEffect(terminal) {
        const codeContent = terminal.querySelector('.code-display, .terminal-content');
        if (!codeContent) return;
        
        const originalText = codeContent.textContent;
        codeContent.textContent = '';
        
        let i = 0;
        const speed = 20; // Milliseconds per character
        
        const typeInterval = setInterval(() => {
            if (i < originalText.length) {
                codeContent.textContent += originalText.charAt(i);
                i++;
            } else {
                clearInterval(typeInterval);
            }
        }, speed);
    }
    
    initializeCopyButtons() {
        const copyButtons = document.querySelectorAll('.copy-button, [data-copy-text]');
        
        copyButtons.forEach(button => {
            button.addEventListener('click', () => {
                const textToCopy = button.dataset.copyText || 
                                 button.getAttribute('data-copy-text') ||
                                 button.closest('.terminal-window')?.querySelector('.code-display')?.textContent;
                
                if (textToCopy) {
                    this.copyToClipboard(textToCopy, button);
                }
            });
        });
    }
    
    copyToClipboard(text, button) {
        navigator.clipboard.writeText(text).then(() => {
            // Visual feedback
            const originalText = button.textContent;
            const originalIcon = button.querySelector('i')?.className;
            
            button.textContent = 'Copied!';
            if (button.querySelector('i')) {
                button.querySelector('i').className = 'fas fa-check';
            }
            
            button.style.background = 'rgba(179, 157, 219, 0.2)';
            button.style.color = 'var(--color-lavender)';
            
            setTimeout(() => {
                button.textContent = originalText;
                if (button.querySelector('i') && originalIcon) {
                    button.querySelector('i').className = originalIcon;
                }
                button.style.background = '';
                button.style.color = '';
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy text:', err);
        });
    }
    
    // ========== TIMELINE COMPONENTS ========== //
    
    initializeTimelineComponents() {
        console.log('📅 Initializing timeline components...');
        
        // Timeline markers
        this.initializeTimelineMarkers();
        
        // Timeline navigation
        this.initializeTimelineNavigation();
        
        // Timeline animations
        this.initializeTimelineAnimations();
        
        console.log('✅ Timeline components initialized');
    }
    
    initializeTimelineMarkers() {
        const markers = document.querySelectorAll('.marker-dot, .timeline-marker');
        
        markers.forEach(marker => {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.transform = 'scale(1.2)';
                        entry.target.style.boxShadow = '0 0 15px var(--color-teal)';
                        
                        setTimeout(() => {
                            entry.target.style.transform = 'scale(1)';
                            entry.target.style.boxShadow = '0 0 8px var(--color-teal)';
                        }, 500);
                    }
                });
            }, { threshold: 0.5 });
            
            observer.observe(marker);
        });
    }
    
    initializeTimelineNavigation() {
        const timelineLinks = document.querySelectorAll('a[href*="#timeline-"]');
        
        timelineLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    this.smoothScrollToElement(targetElement);
                }
            });
        });
    }
    
    initializeTimelineAnimations() {
        const timelineItems = document.querySelectorAll('.timeline-post-card, .timeline-compact-item');
        
        timelineItems.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateX(-30px)';
            
            setTimeout(() => {
                item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                item.style.opacity = '1';
                item.style.transform = 'translateX(0)';
            }, index * 150);
        });
    }
    
    // ========== RESPONSIVE BEHAVIOR ========== //
    
    initializeResponsiveBehavior() {
        console.log('📱 Initializing responsive behavior...');
        
        // Window resize handler
        window.addEventListener('resize', this.debounce(this.handleResize, 250));
        
        // Touch and gesture support
        this.initializeTouchGestures();
        
        // Responsive navigation
        this.initializeResponsiveNavigation();
        
        console.log('✅ Responsive behavior initialized');
    }
    
    handleResize() {
        // Update scroll buttons
        this.updateScrollButtons();
        
        // Adjust grid layouts
        this.adjustGridLayouts();
        
        // Recalculate positions
        this.recalculatePositions();
    }
    
    initializeTouchGestures() {
        // Swipe gestures for category navigation
        const categoriesGrid = document.getElementById('categoriesGrid');
        if (categoriesGrid) {
            this.addSwipeGestures(categoriesGrid, {
                onSwipeLeft: () => this.scrollCategories('right'),
                onSwipeRight: () => this.scrollCategories('left')
            });
        }
        
        // Pull to refresh (if needed)
        this.initializePullToRefresh();
    }
    
    addSwipeGestures(element, callbacks) {
        let startX = 0;
        let startY = 0;
        let distX = 0;
        let distY = 0;
        const threshold = 100;
        
        element.addEventListener('touchstart', (e) => {
            const touch = e.touches[0];
            startX = touch.clientX;
            startY = touch.clientY;
        }, { passive: true });
        
        element.addEventListener('touchend', (e) => {
            const touch = e.changedTouches[0];
            distX = touch.clientX - startX;
            distY = touch.clientY - startY;
            
            if (Math.abs(distX) > Math.abs(distY) && Math.abs(distX) > threshold) {
                if (distX > 0 && callbacks.onSwipeRight) {
                    callbacks.onSwipeRight();
                } else if (distX < 0 && callbacks.onSwipeLeft) {
                    callbacks.onSwipeLeft();
                }
            }
        }, { passive: true });
    }
    
    initializePullToRefresh() {
        let startY = 0;
        let pullDistance = 0;
        let isPulling = false;
        const threshold = 100;
        
        document.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                startY = e.touches[0].clientY;
                isPulling = true;
            }
        }, { passive: true });
        
        document.addEventListener('touchmove', (e) => {
            if (isPulling && window.scrollY === 0) {
                pullDistance = e.touches[0].clientY - startY;
                
                if (pullDistance > 0) {
                    // Visual feedback for pull to refresh
                    document.body.style.transform = `translateY(${Math.min(pullDistance / 3, 50)}px)`;
                }
            }
        }, { passive: true });
        
        document.addEventListener('touchend', () => {
            if (isPulling) {
                document.body.style.transform = '';
                
                if (pullDistance > threshold) {
                    // Trigger refresh
                    window.location.reload();
                }
                
                isPulling = false;
                pullDistance = 0;
            }
        }, { passive: true });
    }
    
    initializeResponsiveNavigation() {
        // Mobile navigation adjustments
        const isMobile = window.innerWidth <= 768;
        
        if (isMobile) {
            // Hide scroll buttons on mobile
            const scrollBtns = document.querySelectorAll('.category-scroll-btn');
            scrollBtns.forEach(btn => {
                btn.style.display = 'none';
            });
            
            // Adjust category grid for touch scrolling
            const categoriesGrid = document.getElementById('categoriesGrid');
            if (categoriesGrid) {
                categoriesGrid.style.justifyContent = 'flex-start';
                categoriesGrid.style.padding = '8px 0';
            }
        }
    }
    
    adjustGridLayouts() {
        const grids = document.querySelectorAll('.datalogs-grid, .category-posts-grid');
        
        grids.forEach(grid => {
            const containerWidth = grid.offsetWidth;
            const cardMinWidth = 350;
            const gap = 32;
            
            const columns = Math.floor((containerWidth + gap) / (cardMinWidth + gap));
            const actualColumns = Math.max(1, columns);
            
            grid.style.gridTemplateColumns = `repeat(${actualColumns}, 1fr)`;
        });
    }
    
    recalculatePositions() {
        // Recalculate any absolute positioned elements
        const fixedElements = document.querySelectorAll('.search-suggestions, .filter-panel');
        
        fixedElements.forEach(element => {
            if (element.style.display !== 'none') {
                // Trigger recalculation
                element.style.display = 'none';
                element.offsetHeight; // Force reflow
                element.style.display = '';
            }
        });
    }
    
    // ========== KEYBOARD NAVIGATION ========== //
    
    initializeKeyboardNavigation() {
        console.log('⌨️ Initializing keyboard navigation...');
        
        // Global keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboardShortcuts);
        
        // Focus management
        this.initializeFocusManagement();
        
        // Tab navigation
        this.initializeTabNavigation();
        
        console.log('✅ Keyboard navigation initialized');
    }
    
    handleKeyboardShortcuts(e) {
        // Search shortcut (Ctrl/Cmd + K)
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            this.focusSearch();
            return;
        }
        
        // Filter shortcut (Ctrl/Cmd + F)
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            e.preventDefault();
            this.toggleFilterPanel();
            return;
        }
        
        // View shortcuts (1, 2, 3 for different views)
        if (!e.ctrlKey && !e.metaKey && !e.altKey) {
            switch (e.key) {
                case '1':
                    this.setView('grid');
                    break;
                case '2':
                    this.setView('list');
                    break;
                case '3':
                    this.setView('timeline');
                    break;
                case 'Escape':
                    this.closeAllPanels();
                    break;
            }
        }
    }
    
    initializeFocusManagement() {
        // Skip links for accessibility
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'skip-link';
        skipLink.textContent = 'Skip to main content';
        skipLink.style.cssText = `
            position: absolute;
            top: -40px;
            left: 6px;
            background: var(--color-lavender);
            color: white;
            padding: 8px;
            text-decoration: none;
            border-radius: 4px;
            z-index: 9999;
        `;
        
        skipLink.addEventListener('focus', () => {
            skipLink.style.top = '6px';
        });
        
        skipLink.addEventListener('blur', () => {
            skipLink.style.top = '-40px';
        });
        
        document.body.insertBefore(skipLink, document.body.firstChild);
    }
    
    initializeTabNavigation() {
        // Make cards focusable
        const cards = document.querySelectorAll('.datalog-card, .category-nav-item');
        
        cards.forEach((card, index) => {
            card.setAttribute('tabindex', '0');
            card.setAttribute('role', 'button');
            
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    card.click();
                }
            });
            
            card.addEventListener('focus', () => {
                card.style.outline = '2px solid var(--color-lavender)';
                card.style.outlineOffset = '2px';
            });
            
            card.addEventListener('blur', () => {
                card.style.outline = 'none';
            });
        });
    }
    
    // ========== SCROLL EFFECTS ========== //
    
    initializeScrollEffects() {
        console.log('📜 Initializing scroll effects...');
        
        // Parallax effects
        this.initializeParallaxEffects();
        
        // Scroll-to-top button
        this.initializeScrollToTop();
        
        // Reading progress (for detail pages)
        this.initializeReadingProgress();
        
        console.log('✅ Scroll effects initialized');
    }
    
    initializeParallaxEffects() {
        const parallaxElements = document.querySelectorAll('.terminal-window, .featured-datalog-container');
        
        window.addEventListener('scroll', this.throttle(() => {
            const scrolled = window.pageYOffset;
            
            parallaxElements.forEach(element => {
                const rate = scrolled * -0.1;
                element.style.transform = `translateY(${rate}px)`;
            });
        }, 16)); // 60fps
    }
    
    initializeScrollToTop() {
        const scrollToTopBtn = document.createElement('button');
        scrollToTopBtn.className = 'scroll-to-top-btn';
        scrollToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
        scrollToTopBtn.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: var(--gradient-glass), rgba(179, 157, 219, 0.2);
            border: 1px solid rgba(179, 157, 219, 0.3);
            color: var(--color-lavender);
            font-size: 1.2rem;
            cursor: pointer;
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        `;
        
        scrollToTopBtn.addEventListener('click', () => {
            this.smoothScrollToTop();
        });
        
        document.body.appendChild(scrollToTopBtn);
        
        // Show/hide based on scroll position
        window.addEventListener('scroll', this.throttle(() => {
            if (window.pageYOffset > 300) {
                scrollToTopBtn.style.opacity = '1';
                scrollToTopBtn.style.visibility = 'visible';
            } else {
                scrollToTopBtn.style.opacity = '0';
                scrollToTopBtn.style.visibility = 'hidden';
            }
        }, 100));
    }
    
    initializeReadingProgress() {
        const progressBar = document.querySelector('.reading-progress-bar .aura-progress-bar');
        if (!progressBar) return;
        
        window.addEventListener('scroll', this.throttle(() => {
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            const scrolled = window.pageYOffset;
            const progress = (scrolled / docHeight) * 100;
            
            progressBar.style.width = `${Math.min(100, Math.max(0, progress))}%`;
        }, 16));
    }
    
    // ========== PERFORMANCE OPTIMIZATIONS ========== //
    
    initializePerformanceOptimizations() {
        console.log('⚡ Initializing performance optimizations...');
        
        // Lazy loading for images
        this.initializeLazyLoading();
        
        // Intersection observer optimizations
        this.optimizeIntersectionObservers();
        
        // Memory management
        this.initializeMemoryManagement();
        
        console.log('✅ Performance optimizations initialized');
    }
    
    initializeLazyLoading() {
        const images = document.querySelectorAll('img[loading="lazy"]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src || img.src;
                        img.classList.add('loaded');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            images.forEach(img => imageObserver.observe(img));
        }
    }
    
    optimizeIntersectionObservers() {
        // Use a single observer for similar elements when possible
        const cardObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, { threshold: 0.1 });
        
        // Observe all cards with a single observer
        const cards = document.querySelectorAll('.datalog-card, .timeline-post-card, .metric-item');
        cards.forEach(card => cardObserver.observe(card));
    }
    
    initializeMemoryManagement() {
        // Clean up event listeners on page unload
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
        
        // Garbage collection for cached data
        setInterval(() => {
            this.cleanupCache();
        }, 300000); // 5 minutes
    }
    
    cleanupCache() {
        const { search } = this.components;
        if (search && search.suggestionCache) {
            // Keep only recent entries
            if (search.suggestionCache.size > 50) {
                const entries = Array.from(search.suggestionCache.entries());
                search.suggestionCache.clear();
                
                // Keep the most recent 25 entries
                entries.slice(-25).forEach(([key, value]) => {
                    search.suggestionCache.set(key, value);
                });
            }
        }
    }
    
    // ========== UTILITY METHODS ========== //
    
    setupGlobalEventListeners() {
        // Global click handler for closing panels
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-suggestions, .filter-panel, .search-panel')) {
                // Close suggestions if clicking outside
                if (this.components.search?.suggestions) {
                    this.hideSearchSuggestions();
                }
            }
        });
        
        // Handle browser back/forward
        window.addEventListener('popstate', () => {
            this.loadUserPreferences();
        });
    }
    
    loadUserPreferences() {
        // Load saved view mode
        const savedView = localStorage.getItem('datalogsViewMode');
        if (savedView) {
            this.state.currentView = savedView;
        }
        
        // Load other preferences
        const savedFilters = localStorage.getItem('datalogsFilters');
        if (savedFilters) {
            try {
                this.state.activeFilters = JSON.parse(savedFilters);
            } catch (e) {
                console.warn('Failed to parse saved filters');
            }
        }
    }
    
    setView(viewType) {
        const button = document.querySelector(`[data-view="${viewType}"]`);
        if (button) {
            button.click();
        }
    }
    
    closeAllPanels() {
        this.closeFilterPanel();
        if (this.state.isSearchPanelOpen) {
            this.toggleSearchPanel();
        }
        this.hideSearchSuggestions();
    }
    
    hasActiveSuggestion() {
        const suggestions = this.components.search?.suggestions;
        return suggestions?.querySelector('.search-suggestion-item.active') !== null;
    }
    
    smoothScroll(element, target, duration) {
        return new Promise(resolve => {
            const start = element.scrollLeft;
            const change = target - start;
            const startTime = performance.now();
            
            function animateScroll(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                
                // Easing function
                const easeOutCubic = 1 - Math.pow(1 - progress, 3);
                
                element.scrollLeft = start + change * easeOutCubic;
                
                if (progress < 1) {
                    requestAnimationFrame(animateScroll);
                } else {
                    resolve();
                }
            }
            
            requestAnimationFrame(animateScroll);
        });
    }
    
    smoothScrollToElement(element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
    
    smoothScrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    cleanup() {
        // Clean up event listeners and observers
        Object.values(this.components).forEach(component => {
            if (component.observer) {
                component.observer.disconnect();
            }
        });
        
        // Clear timers
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        
        console.log('🧹 DataLogs interface cleaned up');
    }
}

// ========== GLOBAL INITIALIZATION ========== //

// Create global instance
const datalogInterface = new DatalogInterface();

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        datalogInterface.init();
    });
} else {
    datalogInterface.init();
}

// Export for global access
window.datalogInterface = datalogInterface;

// ========== DYNAMIC STYLES FOR ANIMATIONS ========== //

// Add dynamic CSS for animations that require JavaScript
const dynamicStyles = document.createElement('style');
dynamicStyles.textContent = `
@keyframes hexRipple {
    0% {
        transform: scale(0);
        opacity: 1;
    }
    100% {
        transform: scale(1);
        opacity: 0;
    }
}

@keyframes cardRipple {
    0% {
        transform: scale(0);
        opacity: 1;
    }
    100% {
        transform: scale(1);
        opacity: 0;
    }
}

.scanning-hex::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, 
        transparent 0%, 
        rgba(179, 157, 219, 0.2) 50%, 
        transparent 100%);
    animation: hexScan 1.5s ease-in-out;
    pointer-events: none;
    z-index: 10;
}

@keyframes hexScan {
    0% { left: -100%; }
    100% { left: 100%; }
}

.scanning-horizontal::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, 
        transparent 0%, 
        rgba(179, 157, 219, 0.15) 50%, 
        transparent 100%);
    animation: scanHorizontal 2s ease-in-out;
    pointer-events: none;
    z-index: 5;
}

@keyframes scanHorizontal {
    0% { left: -100%; }
    100% { left: 100%; }
}

.card-scanning-line {
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, 
        transparent 0%, 
        rgba(179, 157, 219, 0.1) 50%, 
        transparent 100%);
    animation: cardScan 1.5s ease-in-out;
    pointer-events: none;
    z-index: 3;
}

@keyframes cardScan {
    0% { left: -100%; }
    100% { left: 100%; }
}

.animate-in {
    animation: slideInUp 0.6s ease-out;
}

@keyframes slideInUp {
    0% {
        opacity: 0;
        transform: translateY(30px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

.search-focused {
    transform: scale(1.02);
    box-shadow: 0 0 20px rgba(179, 157, 219, 0.3);
}

.terminal-active {
    opacity: 1;
    transform: translateX(0);
}

.loaded {
    opacity: 1;
    transition: opacity 0.3s ease;
}

/* Accessibility improvements */
.skip-link:focus {
    top: 6px !important;
}

@media (prefers-reduced-motion: reduce) {
    .scanning-hex::before,
    .scanning-horizontal::after,
    .card-scanning-line,
    .animate-in {
        animation: none !important;
    }
    
    .datalog-card:hover,
    .category-nav-item:hover,
    .timeline-post-card:hover {
        transform: none !important;
    }
}

/* High contrast mode */
@media (prefers-contrast: high) {
    .datalog-card,
    .category-hexagon.glass-hex,
    .terminal-window {
        border-width: 2px !important;
        backdrop-filter: none !important;
    }
}

/* Dark mode enhancements */
@media (prefers-color-scheme: dark) {
    .scroll-to-top-btn {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
}
`;

document.head.appendChild(dynamicStyles);

// ========== COMPATIBILITY AND FALLBACKS ========== //

// Polyfill for IntersectionObserver
if (!window.IntersectionObserver) {
    // Simple fallback for older browsers
    window.IntersectionObserver = class {
        constructor(callback) {
            this.callback = callback;
        }
        observe(element) {
            // Trigger immediately for older browsers
            this.callback([{ target: element, isIntersecting: true }]);
        }
        unobserve() {}
        disconnect() {}
    };
}

// Polyfill for scrollTo with behavior
if (!Element.prototype.scrollTo) {
    Element.prototype.scrollTo = function(options) {
        if (typeof options === 'object') {
            this.scrollLeft = options.left || this.scrollLeft;
            this.scrollTop = options.top || this.scrollTop;
        }
    };
}

// Clipboard API fallback
if (!navigator.clipboard) {
    navigator.clipboard = {
        writeText: function(text) {
            return new Promise((resolve, reject) => {
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                try {
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    resolve();
                } catch (err) {
                    document.body.removeChild(textArea);
                    reject(err);
                }
            });
        }
    };
}

// ========== LEGACY BROWSER SUPPORT ========== //

// Support for older browsers that don't have arrow functions
if (!window.Set) {
    window.Set = function() {
        this.items = [];
        this.add = function(item) {
            if (this.items.indexOf(item) === -1) {
                this.items.push(item);
            }
        };
        this.has = function(item) {
            return this.items.indexOf(item) !== -1;
        };
        this.clear = function() {
            this.items = [];
        };
        Object.defineProperty(this, 'size', {
            get: function() { return this.items.length; }
        });
    };
}

// Support for Map if not available
if (!window.Map) {
    window.Map = function() {
        this.keys = [];
        this.values = [];
        this.set = function(key, value) {
            const index = this.keys.indexOf(key);
            if (index === -1) {
                this.keys.push(key);
                this.values.push(value);
            } else {
                this.values[index] = value;
            }
        };
        this.get = function(key) {
            const index = this.keys.indexOf(key);
            return index !== -1 ? this.values[index] : undefined;
        };
        this.has = function(key) {
            return this.keys.indexOf(key) !== -1;
        };
        this.clear = function() {
            this.keys = [];
            this.values = [];
        };
        Object.defineProperty(this, 'size', {
            get: function() { return this.keys.length; }
        });
    };
}

// ========== GLOBAL HELPER FUNCTIONS ========== //

// Helper functions that can be called from templates
window.initDatalogsInterface = function() {
    if (window.datalogInterface && !window.datalogInterface.isInitialized) {
        window.datalogInterface.init();
    }
};

window.updateCategoryScroll = function() {
    if (window.datalogInterface && window.datalogInterface.updateScrollButtons) {
        window.datalogInterface.updateScrollButtons();
    }
};

window.focusDatalogSearch = function() {
    if (window.datalogInterface && window.datalogInterface.focusSearch) {
        window.datalogInterface.focusSearch();
    }
};

window.toggleDatalogFilters = function() {
    if (window.datalogInterface && window.datalogInterface.toggleFilterPanel) {
        window.datalogInterface.toggleFilterPanel();
    }
};

window.selectSuggestion = function(text, url) {
    if (window.datalogInterface && window.datalogInterface.selectSuggestion) {
        window.datalogInterface.selectSuggestion(text, url);
    }
};

// ========== DEBUGGING UTILITIES ========== //

// Debug mode functions
window.enableDatalogDebug = function() {
    if (window.datalogInterface) {
        window.datalogInterface.config.enableDebugMode = true;
        document.body.classList.add('debug');
        console.log('🐛 DataLog debug mode enabled');
    }
};

window.disableDatalogDebug = function() {
    if (window.datalogInterface) {
        window.datalogInterface.config.enableDebugMode = false;
        document.body.classList.remove('debug');
        console.log('✅ DataLog debug mode disabled');
    }
};

window.getDatalogState = function() {
    return window.datalogInterface ? window.datalogInterface.state : null;
};

// Performance monitoring
if (window.performance && window.performance.mark) {
    window.performance.mark('datalogs-js-end');
    
    window.addEventListener('load', () => {
        setTimeout(() => {
            try {
                window.performance.measure('datalogs-js-execution', 'datalogs-js-start', 'datalogs-js-end');
                const measure = window.performance.getEntriesByName('datalogs-js-execution')[0];
                console.log(`📊 DataLogs JS execution time: ${measure.duration.toFixed(2)}ms`);
            } catch (e) {
                // Silently fail if performance API is not fully supported
            }
        }, 100);
    });
}

// Mark start of execution
if (window.performance && window.performance.mark) {
    window.performance.mark('datalogs-js-start');
}

console.log('🚀 DataLogs consolidated JavaScript loaded successfully');
console.log('📋 Available functions: initDatalogsInterface(), updateCategoryScroll(), focusDatalogSearch(), toggleDatalogFilters()');
console.log('🐛 Debug functions: enableDatalogDebug(), disableDatalogDebug(), getDatalogState()');

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DatalogInterface;
}

if (typeof define === 'function' && define.amd) {
    define(function() {
        return DatalogInterface;
    });
}