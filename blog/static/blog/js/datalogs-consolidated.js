/**
 * AURA DataLogs - Master Consolidated JavaScript (Cleaned & Optimized)
 * Advanced User Repository & Archive - Complete DataLogs Functionality
 * Version: 3.2.0 - Cleaned, optimized, and error-free
 * 
 * This file contains ALL DataLogs JavaScript in organized modules:
 * - Glass hexagon navigation with smooth scrolling
 * - Enhanced search with real-time suggestions
 * - Filter panels and interactive controls
 * - Timeline animations and interactions
 * - Card hover effects and state management
 * - View toggles and sorting functionality
 * - Terminal code display enhancements
 * - Post detail functionality (TOC, reading progress)
 * - Responsive behavior and touch support
 */

// ========== PERFORMANCE MARKING ========== //
if (window.performance && window.performance.mark) {
    window.performance.mark('datalogs-js-start');
}

// ========== DATALOG INTERFACE CORE ========== //

class DatalogInterface {
    constructor() {
        this.isInitialized = false;
        this.components = {};
        this.observers = new Set();
        this.timers = new Set();
        this.state = {
            currentView: 'grid',
            searchQuery: '',
            activeFilters: {},
            currentCategory: null,
            isFilterPanelOpen: false,
            isSearchPanelOpen: false,
            currentPage: 'list' // list, detail, category, archive, search
        };
        
        // Configuration
        this.config = {
            animationDuration: 300,
            debounceDelay: 300,
            scrollDuration: 500,
            maxSearchSuggestions: 5,
            cardAnimationDelay: 100,
            enableDebugMode: false,
            typewriterSpeed: 20, // ms per character
            tocUpdateThrottle: 100 // TOC scroll update throttle
        };
        
        // Bind methods to maintain context
        this.init = this.init.bind(this);
        this.handleResize = this.handleResize.bind(this);
        this.handleKeyboardShortcuts = this.handleKeyboardShortcuts.bind(this);
        this.cleanup = this.cleanup.bind(this);
    }
    
    // ========== INITIALIZATION ========== //
    
    init() {
        if (this.isInitialized) return;
        
        console.log('🚀 DataLogs interface initializing...');
        
        try {
            // Detect page type first
            this.detectPageType();
            
            // Initialize core components (always needed)
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
            this.enhanceReadingProgressIndicators();
            
            // Initialize page-specific components
            if (this.state.currentPage === 'detail') {
                this.initializePostDetail();
            }
            
            // Set up global event listeners
            this.setupGlobalEventListeners();
            
            // Load saved preferences
            this.loadUserPreferences();
            
            this.isInitialized = true;
            console.log('✅ DataLogs interface initialized successfully');
            
            // Dispatch custom event
            window.dispatchEvent(new CustomEvent('datalogsInitialized', {
                detail: { interface: this, pageType: this.state.currentPage }
            }));
            
        } catch (error) {
            console.error('❌ DataLogs initialization failed:', error);
        }
    }
    
    detectPageType() {
        const body = document.body;
        
        if (body.classList.contains('post-detail') || document.getElementById('postContent')) {
            this.state.currentPage = 'detail';
        } else if (body.classList.contains('category-view')) {
            this.state.currentPage = 'category';
        } else if (body.classList.contains('archive-view')) {
            this.state.currentPage = 'archive';
        } else if (body.classList.contains('search-results')) {
            this.state.currentPage = 'search';
        } else {
            this.state.currentPage = 'list';
        }
        
        console.log(`📄 Detected page type: ${this.state.currentPage}`);
    }
    
    // ========== POST DETAIL FUNCTIONALITY ========== //
    
    initializePostDetail() {
        console.log('📖 Initializing post detail functionality...');
        
        // Initialize all post detail components
        this.generateTableOfContents();
        this.initializeReadingProgress();
        this.initializeSmoothScrolling();
        this.initializePostCopyButtons();
        this.enhanceReadingProgressIndicators();
        
        console.log('✅ Post detail functionality initialized');
    }
    
    generateTableOfContents() {
        const tocNav = document.getElementById('tocNav');
        const postContent = document.getElementById('postContent');
        
        if (!tocNav || !postContent) return;
        
        console.log('📑 Generating table of contents...');
        
        // Find all headings in the content
        const headings = postContent.querySelectorAll('h1, h2, h3, h4, h5, h6');
        
        if (headings.length === 0) {
            tocNav.innerHTML = `
                <div class="toc-empty">
                    <i class="fas fa-info-circle"></i>
                    <span>No headings found in this entry</span>
                </div>
            `;
            return;
        }
        
        // Generate TOC HTML
        let tocHTML = '';
        headings.forEach((heading, index) => {
            const level = parseInt(heading.tagName.substring(1));
            const text = heading.textContent.trim();
            const id = `heading-${index}`;
            
            // Add ID to heading for linking
            heading.id = id;
            
            // Create indent markers based on level
            const indent = '›'.repeat(Math.max(1, level - 1));
            
            tocHTML += `
                <a href="#${id}" class="toc-link toc-level-${level}" data-level="${level}">
                    <span class="toc-marker">${indent}</span>
                    <span class="toc-text">${text}</span>
                </a>
            `;
        });
        
        tocNav.innerHTML = tocHTML;
        
        // Store reference for scroll tracking
        this.components.toc = {
            nav: tocNav,
            headings: headings,
            links: tocNav.querySelectorAll('.toc-link')
        };
        
        // Add click handlers for smooth scrolling
        this.components.toc.links.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    // Remove active class from all links
                    this.components.toc.links.forEach(l => l.classList.remove('active'));
                    // Add active class to clicked link
                    link.classList.add('active');
                    
                    // Smooth scroll to target
                    this.smoothScrollToElement(targetElement);
                }
            });
        });
        
        const scrollHandler = this.throttle(() => {
            this.updateTOCActiveState();
        }, this.config.tocUpdateThrottle);
        
        window.addEventListener('scroll', scrollHandler);
        this.timers.add(() => window.removeEventListener('scroll', scrollHandler));
        
        console.log(`✅ Generated TOC with ${headings.length} headings`);
    }
    
    updateTOCActiveState() {
        if (!this.components.toc) return;
        
        const { headings, links } = this.components.toc;
        const scrollPos = window.pageYOffset + 100;
        
        let current = '';
        headings.forEach((heading, index) => {
            if (heading.offsetTop <= scrollPos) {
                current = `heading-${index}`;
            }
        });
        
        // Update active state
        links.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    }
    
    initializeSmoothScrolling() {
        // Smooth scroll for all anchor links
        const anchorLinks = document.querySelectorAll('a[href^="#"]');
        
        anchorLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                const targetId = link.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    e.preventDefault();
                    this.smoothScrollToElement(targetElement);
                }
            });
        });
    }
    
    initializePostCopyButtons() {
        const copyButtons = document.querySelectorAll('.copy-button, [data-copy-text]');
        
        copyButtons.forEach(button => {
            button.addEventListener('click', () => {
                const textToCopy = button.dataset.copyText || 
                                 button.getAttribute('data-copy-text') ||
                                 button.closest('.terminal-window')?.querySelector('.code-display')?.textContent ||
                                 button.closest('pre')?.textContent;
                
                if (textToCopy) {
                    this.copyToClipboard(textToCopy, button);
                }
            });
        });
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
        
        this.initializeTouchNavigation(scrollContainer);
        
        const scrollHandler = this.debounce(() => this.updateScrollButtons(), 100);
        scrollContainer.addEventListener('scroll', scrollHandler);
        
        const timer = setTimeout(() => this.updateScrollButtons(), 100);
        this.timers.add(() => clearTimeout(timer));
        
        const resizeHandler = this.debounce(() => this.updateScrollButtons(), 200);
        window.addEventListener('resize', resizeHandler);
        this.timers.add(() => window.removeEventListener('resize', resizeHandler));
        
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
        if (!nav || !nav.container || !nav.leftBtn || !nav.rightBtn) return;
        
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
            const walk = (startX - x) * 2;
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
            
            const timer = setTimeout(() => {
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, index * 100);
            this.timers.add(() => clearTimeout(timer));
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
                const timer = setTimeout(() => item.classList.remove('scanning-hex'), 1500);
                this.timers.add(() => clearTimeout(timer));
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
        
        const timer = setTimeout(() => ripple.remove(), 600);
        this.timers.add(() => clearTimeout(timer));
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
        
        const shortcutHandler = (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.focusSearch();
            }
        };
        
        document.addEventListener('keydown', shortcutHandler);
        this.timers.add(() => document.removeEventListener('keydown', shortcutHandler));
        
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
                this.timers.add(() => clearTimeout(searchTimeout));
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
            const timer = setTimeout(() => {
                this.hideSearchSuggestions();
                input.closest('.search-input-wrapper')?.classList.remove('search-focused');
            }, 200);
            this.timers.add(() => clearTimeout(timer));
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
    
    initializeSearchKeyboardNav(suggestionsContainer) {
        const keyHandler = (e) => {
            if (!suggestionsContainer.classList.contains('show')) return;
            
            const suggestions = suggestionsContainer.querySelectorAll('.search-suggestion-item');
            const currentActive = suggestionsContainer.querySelector('.search-suggestion-item.active');
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (currentActive) {
                    currentActive.classList.remove('active');
                    const next = currentActive.nextElementSibling;
                    if (next) {
                        next.classList.add('active');
                    } else {
                        suggestions[0]?.classList.add('active');
                    }
                } else {
                    suggestions[0]?.classList.add('active');
                }
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (currentActive) {
                    currentActive.classList.remove('active');
                    const prev = currentActive.previousElementSibling;
                    if (prev) {
                        prev.classList.add('active');
                    } else {
                        suggestions[suggestions.length - 1]?.classList.add('active');
                    }
                } else {
                    suggestions[suggestions.length - 1]?.classList.add('active');
                }
            } else if (e.key === 'Enter') {
                if (currentActive) {
                    e.preventDefault();
                    currentActive.click();
                }
            }
        };
        
        document.addEventListener('keydown', keyHandler);
        this.timers.add(() => document.removeEventListener('keydown', keyHandler));
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
        
        const timer = setTimeout(() => {
            const suggestionsData = this.generateSearchSuggestions(query);
            suggestionCache.set(query, suggestionsData);
            this.displaySearchSuggestions(suggestionsData);
        }, 200);
        this.timers.add(() => clearTimeout(timer));
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
        suggestions.offsetHeight; // Force reflow
        suggestions.classList.add('show');
    }
    
    hideSearchSuggestions() {
        const { suggestions } = this.components.search;
        if (!suggestions) return;
        
        suggestions.classList.remove('show');
        const timer = setTimeout(() => {
            suggestions.style.display = 'none';
        }, 200);
        this.timers.add(() => clearTimeout(timer));
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
                const timer = setTimeout(() => searchInput.focus(), 100);
                this.timers.add(() => clearTimeout(timer));
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
        
        const clickHandler = (e) => {
            if (filterPanel && 
                this.state.isFilterPanelOpen && 
                !filterPanel.contains(e.target) && 
                !filterToggle?.contains(e.target)) {
                this.closeFilterPanel();
            }
        };
        
        document.addEventListener('click', clickHandler);
        this.timers.add(() => document.removeEventListener('click', clickHandler));
        
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
            panel.offsetHeight; // Force reflow
            panel.classList.add('show');
            toggle.classList.add('active');
            this.state.isFilterPanelOpen = true;
            
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
        
        const timer = setTimeout(() => {
            panel.style.display = 'none';
        }, this.config.animationDuration);
        this.timers.add(() => clearTimeout(timer));
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
                const timer = setTimeout(() => {
                    filter.style.transform = '';
                }, 150);
                this.timers.add(() => clearTimeout(timer));
                
                // Track filter usage
                const filterType = filter.textContent.trim();
                console.log('Filter clicked:', filterType);
            });
        });
    }
    
    // ========== GRID CONTROLS ========== //
    
    initializeGridControls() {
        const viewToggleButtons = document.querySelectorAll('.view-toggle-btn, .view-btn');
        const sortSelects = document.querySelectorAll('#datalogsSort, #categorySort, #archiveSort, #resultsSort');
        
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
            '.datalogs-grid, .datalogs-main-content, #datalogsGrid, .category-posts-grid, #searchResultsGrid, #archiveTimelineContainer'
        );
        
        gridContainers.forEach(container => {
            if (!container) return;
            
            // Add loading state
            container.style.opacity = '0.7';
            container.style.pointerEvents = 'none';
            
            const timer = setTimeout(() => {
                container.className = container.className.replace(/\b\w+-view\b/g, '');
                container.classList.add(`${viewType}-view`);
                
                // Restore normal state
                container.style.opacity = '1';
                container.style.pointerEvents = 'auto';
                
                // Re-animate cards
                this.animateCardsEntrance(container);
                
            }, 200);
            this.timers.add(() => clearTimeout(timer));
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
            
            const timer = setTimeout(() => {
                container.style.opacity = '1';
                container.style.pointerEvents = 'auto';
            }, 500);
            this.timers.add(() => clearTimeout(timer));
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
                if (e.target.closest('a, button')) return;
                
                // Create ripple effect
                this.createCardRipple(card, e);
                
                // Navigate to post
                const link = card.querySelector('.datalog-title a, .read-more-btn, .item-link');
                if (link) {
                    const timer = setTimeout(() => {
                        link.click();
                    }, 200);
                    this.timers.add(() => clearTimeout(timer));
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
                
                const timer = setTimeout(() => scanLine.remove(), 1500);
                this.timers.add(() => clearTimeout(timer));
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
        
        const timer = setTimeout(() => ripple.remove(), 600);
        this.timers.add(() => clearTimeout(timer));
    }
    
    observeCardEntrance(card, index) {
        // Set initial state
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const timer = setTimeout(() => {
                        entry.target.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, index * this.config.cardAnimationDelay);
                    this.timers.add(() => clearTimeout(timer));
                    
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        observer.observe(card);
        this.observers.add(observer);
    }
    
    animateCardsEntrance(container) {
        const cards = container.querySelectorAll('.datalog-card, .timeline-post-card');
        
        cards.forEach((card, index) => {
            card.style.opacity = '0.7';
            card.style.transform = 'scale(0.95)';
            
            const timer = setTimeout(() => {
                card.style.transition = 'all 0.3s ease';
                card.style.opacity = '1';
                card.style.transform = 'scale(1)';
            }, index * 50);
            this.timers.add(() => clearTimeout(timer));
        });
    }
    
    // ========== TERMINAL DISPLAY ENHANCEMENTS ========== //
    
    initializeTerminalDisplay() {
        const terminals = document.querySelectorAll('.terminal-window, .featured-terminal-container');
        
        console.log('💻 Initializing terminal displays...');
        
        terminals.forEach(terminal => {
            this.enhanceTerminalUnified(terminal);
        });
        
        // Copy button functionality
        this.initializeCopyButtons();
        
        console.log('✅ Terminal displays initialized');
    }
    
    // ========== UNIFIED TERMINAL ENHANCEMENT ========== //

    enhanceTerminalUnified(terminal) {
        // Check if terminal has code content that should be animated
        const codeDisplay = terminal.querySelector('.code-display, .terminal-content');
        const hasHighlighting = codeDisplay?.querySelector('.highlighted, .highlight, pre code');
        const shouldAnimate = this.shouldAnimateTerminal(terminal, codeDisplay);
        
        // Add terminal activation effect
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('terminal-active');
                    
                    if (shouldAnimate && codeDisplay && !codeDisplay.dataset.animated) {
                        codeDisplay.dataset.animated = 'true';
                        
                        if (hasHighlighting) {
                            // Use highlighting-aware animation
                            this.animateHighlightedCode(codeDisplay);
                        } else {
                            // Use simple typewriter effect
                            this.addTypingEffect(codeDisplay);
                        }
                    }
                    
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.3 });
        
        observer.observe(terminal);
        this.observers.add(observer);
        
        // Terminal button interactions (unchanged)
        const buttons = terminal.querySelectorAll('.terminal-button');
        buttons.forEach(button => {
            button.addEventListener('click', () => {
                button.style.transform = 'scale(0.8)';
                const timer = setTimeout(() => {
                    button.style.transform = 'scale(1)';
                }, 100);
                this.timers.add(() => clearTimeout(timer));
            });
        });
    }
    
    // ========== ANIMATION DECISION LOGIC ========== //

    shouldAnimateTerminal(terminal, codeDisplay) {
        // Don't animate if no code content
        if (!codeDisplay) return false;
        
        // Don't animate if content is too long (performance)
        const textContent = codeDisplay.textContent || '';
        if (textContent.length > 500) return false;
        
        // Don't animate if user prefers reduced motion
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return false;
        
        // Don't animate if already animated
        if (codeDisplay.dataset.animated) return false;
        
        // Animate for all page types (remove page-specific logic)
        return true;
    }

    // ========== HIGHLIGHTING-AWARE ANIMATION ========== //

    animateHighlightedCode(codeElement) {
        // Store original highlighted HTML
        const originalHTML = codeElement.innerHTML;
        const textContent = codeElement.textContent || '';
        
        // Create a temporary element to extract plain text properly
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = originalHTML;
        const plainText = tempDiv.textContent || tempDiv.innerText || '';
        
        // Start with empty content
        codeElement.innerHTML = '';
        
        let i = 0;
        
        const typeCharacter = () => {
            if (i < plainText.length) {
                // Add character by character, preserving basic structure
                const currentText = plainText.substring(0, i + 1);
                
                // For highlighting, we'll add characters as plain text first
                codeElement.textContent = currentText;
                
                i++;
                const timer = setTimeout(typeCharacter, this.config.typewriterSpeed);
                this.timers.add(() => clearTimeout(timer));
            } else {
                // Animation complete - restore full highlighting
                const timer = setTimeout(() => {
                    codeElement.innerHTML = originalHTML;
                    // Add completion effect
                    codeElement.classList.add('animation-complete');
                }, 200);
                this.timers.add(() => clearTimeout(timer));
            }
        };
        
        // Start animation after delay
        const timer = setTimeout(typeCharacter, 500);
        this.timers.add(() => clearTimeout(timer));
    }

    // ========== SIMPLE TYPEWRITER EFFECT (for non-highlighted code) ========== //

    addTypingEffect(codeElement) {
        const originalHTML = codeElement.innerHTML;
        const textContent = codeElement.textContent || '';
        
        // Don't animate if content is too long
        if (textContent.length > 500) return;
        
        codeElement.innerHTML = '';
        
        let i = 0;
        
        const typeCharacter = () => {
            if (i < textContent.length) {
                codeElement.textContent += textContent.charAt(i);
                i++;
                const timer = setTimeout(typeCharacter, this.config.typewriterSpeed);
                this.timers.add(() => clearTimeout(timer));
            } else {
                // Restore original HTML in case there was any formatting
                codeElement.innerHTML = originalHTML;
                codeElement.classList.add('animation-complete');
            }
        };
        
        const timer = setTimeout(typeCharacter, 500);
        this.timers.add(() => clearTimeout(timer));
    }
    
    initializeCopyButtons() {
        const copyButtons = document.querySelectorAll('.copy-button, [data-copy-text]');
        
        copyButtons.forEach(button => {
            button.addEventListener('click', () => {
                const textToCopy = button.dataset.copyText || 
                                 button.getAttribute('data-copy-text') ||
                                 button.closest('.terminal-window')?.querySelector('.code-display')?.textContent ||
                                 button.closest('pre')?.textContent;
                
                if (textToCopy) {
                    this.copyToClipboard(textToCopy, button);
                }
            });
        });
    }
    
    copyToClipboard(text, button) {
        navigator.clipboard.writeText(text).then(() => {
            // Visual feedback
            const originalContent = button.innerHTML;
            const originalText = button.textContent;
            
            if (button.querySelector('i')) {
                button.innerHTML = '<i class="fas fa-check"></i> Copied!';
            } else {
                button.textContent = 'Copied!';
            }
            
            button.style.background = 'rgba(179, 157, 219, 0.2)';
            button.style.color = 'var(--color-lavender)';
            
            const timer = setTimeout(() => {
                if (originalContent.includes('<')) {
                    button.innerHTML = originalContent;
                } else {
                    button.textContent = originalText;
                }
                button.style.background = '';
                button.style.color = '';
            }, 2000);
            this.timers.add(() => clearTimeout(timer));
        }).catch(err => {
            console.error('Failed to copy text:', err);
            
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            
            try {
                document.execCommand('copy');
                button.innerHTML = '<i class="fas fa-check"></i> Copied!';
            } catch (err) {
                button.innerHTML = '<i class="fas fa-exclamation"></i> Copy failed';
            }
            
            document.body.removeChild(textArea);
            
            const timer = setTimeout(() => {
                button.innerHTML = '<i class="fas fa-copy"></i> Copy Code';
            }, 2000);
            this.timers.add(() => clearTimeout(timer));
        });
    }
    
    // ========== TIMELINE COMPONENTS ========== //
    
    initializeTimelineComponents() {
        console.log('📅 Initializing timeline components...');
        
        this.initializeTimelineMarkers();
        this.initializeTimelineNavigation();
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
                        
                        const timer = setTimeout(() => {
                            entry.target.style.transform = 'scale(1)';
                            entry.target.style.boxShadow = '0 0 8px var(--color-teal)';
                        }, 500);
                        this.timers.add(() => clearTimeout(timer));
                    }
                });
            }, { threshold: 0.5 });
            
            observer.observe(marker);
            this.observers.add(observer);
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
            
            const timer = setTimeout(() => {
                item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                item.style.opacity = '1';
                item.style.transform = 'translateX(0)';
            }, index * 150);
            this.timers.add(() => clearTimeout(timer));
        });
    }
    
    // ========== READING PROGRESS ========== //
    
    initializeReadingProgress() {
        const progressBar = document.querySelector('.reading-progress-bar .aura-progress-bar');
        if (!progressBar) return;
        
        console.log('📖 Initializing reading progress...');
        
        const updateProgress = () => {
            if (this.state.currentPage === 'detail') {
                // Post detail specific progress calculation
                const postContent = document.getElementById('postContent');
                if (!postContent) return;
                
                const postTop = postContent.offsetTop;
                //const postHeight = postContent.offsetHeight;
                const windowHeight = window.innerHeight;
                const scrollTop = window.pageYOffset;

                const docHeight = document.documentElement.scrollHeight - window.innerHeight;
               
                // TWEAKED: Calculate progress based on post content
                const progress = Math.min(100, Math.max(0, 
                    ((scrollTop - postTop + windowHeight) / docHeight) * 100
                ));
                //console.log('tryProg = ' + tryProg);
                
                progressBar.style.width = `${progress}%`;
                
                // Update text if present
                const progressText = progressBar.closest('.aura-progress-container')?.querySelector('.progress-text');
                if (progressText) {
                    progressText.textContent = `${Math.round(progress)}%`;
                }
            } else {
                // General page progress
                const docHeight = document.documentElement.scrollHeight - window.innerHeight;
                const scrolled = window.pageYOffset;
                const progress = (scrolled / docHeight) * 100;
                
                progressBar.style.width = `${Math.min(100, Math.max(0, progress))}%`;
            }
        };
        
        const scrollHandler = this.throttle(updateProgress, 50);
        window.addEventListener('scroll', scrollHandler);
        this.timers.add(() => window.removeEventListener('scroll', scrollHandler));
        updateProgress();
    }

    // ========== ENHANCED READING PROGRESS (EXTENDS EXISTING) ==========

    enhanceReadingProgressIndicators() {
        const progressIndicators = document.querySelectorAll('.reading-progress-indicator');
        
        progressIndicators.forEach(indicator => {
            this.initializeProgressIndicator(indicator);
        });
        
        console.log(`✅ Enhanced ${progressIndicators.length} reading progress indicators`);
    }

    initializeProgressIndicator(indicator) {
        try {
            const config = JSON.parse(indicator.dataset.config || '{}');
            const targetElement = document.getElementById(config.target_element) || 
                                document.querySelector(config.target_element) || 
                                document.body;
            
            // Create progress tracker
            const progressTracker = {
                indicator: indicator,
                config: config,
                target: targetElement,
                isVisible: false,
                lastProgress: 0,
                startTime: Date.now(),
                totalReadingTime: config.total_reading_time || 0,
                elements: this.getProgressElements(indicator),
                updateTimer: null,
            };
            
            // Store reference for cleanup
            this.components.progressTrackers = this.components.progressTrackers || [];
            this.components.progressTrackers.push(progressTracker);
            
            // Initialize based on style
            this.setupProgressTracker(progressTracker);
            
            // Start tracking
            this.startProgressTracking(progressTracker);
            
        } catch (error) {
            console.warn('Failed to initialize progress indicator:', error);
        }
    }

    getProgressElements(indicator) {
        return {
            progressBar: indicator.querySelector('.aura-progress-bar'),
            circleProgress: indicator.querySelector('.circular-progress-svg .progress-circle'),
            percentageText: indicator.querySelector('.circle-percentage, .minimal-percentage, .floating-percentage'),
            timeElapsed: indicator.querySelector('.time-elapsed'),
            timeRemaining: indicator.querySelector('.time-remaining'),
            positionCurrent: indicator.querySelector('.position-current'),
            positionIndicator: indicator.querySelector('.position-indicator'),
            motivationMessage: indicator.querySelector('.motivation-message'),
        };
    }

    setupProgressTracker(tracker) {
        const { config, indicator, elements } = tracker;
        
        // Set initial visibility based on threshold
        if (config.threshold > 0) {
            indicator.style.opacity = '0';
            indicator.style.visibility = 'hidden';
            indicator.classList.add('progress-hidden');
        }
        
        // Setup animations if enabled
        if (config.animate) {
            indicator.classList.add('progress-animated');
        }
        
        if (config.smooth) {
            indicator.classList.add('progress-smooth');
        }
        
        // Initialize ARIA attributes
        indicator.setAttribute('aria-valuemin', '0');
        indicator.setAttribute('aria-valuemax', '100');
        indicator.setAttribute('aria-valuenow', '0');
        
        // Set up position tracking if needed
        if (config.show_position && tracker.target !== document.body) {
            this.calculateContentMetrics(tracker);
        }
    }

    calculateContentMetrics(tracker) {
        const content = tracker.target.textContent || '';
        tracker.contentMetrics = {
            totalWords: content.split(/\s+/).filter(word => word.length > 0).length,
            totalCharacters: content.length,
            paragraphs: content.split(/\n\s*\n/).length,
        };
    }

    startProgressTracking(tracker) {
        const { config } = tracker;
        const updateFrequency = config.update_frequency || 100;
        
        // Throttled scroll handler
        const scrollHandler = this.throttle(() => {
            this.updateProgress(tracker);
        }, updateFrequency);
        
        // Start tracking
        window.addEventListener('scroll', scrollHandler);
        window.addEventListener('resize', scrollHandler);
        
        // Store cleanup function
        const cleanup = () => {
            window.removeEventListener('scroll', scrollHandler);
            window.removeEventListener('resize', scrollHandler);
            if (tracker.updateTimer) {
                clearInterval(tracker.updateTimer);
            }
        };
        
        this.timers.add(cleanup);
        
        // Initial update
        this.updateProgress(tracker);
        
        // Setup time tracking for reading time estimates
        if (config.show_time && tracker.totalReadingTime > 0) {
            this.startTimeTracking(tracker);
        }
    }

    updateProgress(tracker) {
        const { config, target, elements, indicator } = tracker;
        
        // Calculate scroll progress
        const progress = this.calculateScrollProgress(target);
        
        // Check visibility threshold
        if (config.threshold > 0) {
            const shouldShow = progress >= (config.threshold * 100);
            this.toggleProgressVisibility(tracker, shouldShow);
        }
        
        // Update progress if changed significantly
        if (Math.abs(progress - tracker.lastProgress) > 0.5) {
            this.updateProgressDisplay(tracker, progress);
            tracker.lastProgress = progress;
            
            // Update reading state
            this.updateReadingState(tracker, progress);
        }
        
        // Update ARIA
        indicator.setAttribute('aria-valuenow', Math.round(progress));
    }

    calculateScrollProgress(target) {
        if (target === document.body) {
            // Whole page progress
            const windowHeight = window.innerHeight;
            const documentHeight = document.documentElement.scrollHeight - windowHeight;
            const scrolled = window.pageYOffset;
            return Math.min(100, Math.max(0, (scrolled / documentHeight) * 100));
        } else {
            // Element-specific progress
            const rect = target.getBoundingClientRect();
            const windowHeight = window.innerHeight;
            const elementTop = window.pageYOffset + rect.top;
            const elementHeight = rect.height;
            const scrolled = window.pageYOffset;
            
            // Calculate progress through the element
            const startReading = elementTop - windowHeight * 0.1; // Start when 10% visible
            const finishReading = elementTop + elementHeight;
            
            if (scrolled < startReading) return 0;
            if (scrolled > finishReading) return 100;
            
            return ((scrolled - startReading) / (finishReading - startReading)) * 100;
        }
    }

    toggleProgressVisibility(tracker, shouldShow) {
        const { indicator } = tracker;
        
        if (shouldShow && !tracker.isVisible) {
            indicator.classList.remove('progress-hidden');
            indicator.classList.add('progress-visible');
            indicator.style.opacity = '1';
            indicator.style.visibility = 'visible';
            tracker.isVisible = true;
        } else if (!shouldShow && tracker.isVisible) {
            indicator.classList.add('progress-hidden');
            indicator.classList.remove('progress-visible');
            indicator.style.opacity = '0';
            indicator.style.visibility = 'hidden';
            tracker.isVisible = false;
        }
    }

    updateProgressDisplay(tracker, progress) {
        const { elements, config } = tracker;
        
        // Update progress bar
        if (elements.progressBar) {
            elements.progressBar.style.width = `${progress}%`;
        }
        
        // Update circular progress
        if (elements.circleProgress) {
            const circumference = 2 * Math.PI * 40; // Assuming 40px radius
            const offset = circumference - (progress / 100 * circumference);
            elements.circleProgress.style.strokeDashoffset = offset;
        }
        
        // Update percentage text
        if (elements.percentageText && config.show_percentage) {
            elements.percentageText.textContent = `${Math.round(progress)}%`;
        }
        
        // Update position indicator
        if (elements.positionIndicator) {
            elements.positionIndicator.style.width = `${progress}%`;
        }
        
        // Update word position
        if (elements.positionCurrent && tracker.contentMetrics) {
            const currentWords = Math.round((progress / 100) * tracker.contentMetrics.totalWords);
            elements.positionCurrent.textContent = this.formatNumber(currentWords);
        }
    }

    startTimeTracking(tracker) {
        const { config, elements } = tracker;
        
        if (!config.show_time || !elements.timeElapsed) return;
        
        const updateTimeDisplay = () => {
            const elapsed = (Date.now() - tracker.startTime) / 1000 / 60; // minutes
            const elapsedFormatted = this.formatDuration(Math.round(elapsed));
            
            if (elements.timeElapsed) {
                elements.timeElapsed.textContent = elapsedFormatted;
            }
            
            // Update remaining time estimate
            if (elements.timeRemaining && tracker.totalReadingTime > 0) {
                const progressRatio = tracker.lastProgress / 100;
                let remainingTime;
                
                if (progressRatio > 0.1) {
                    // Estimate based on actual reading speed
                    const estimatedTotalTime = elapsed / progressRatio;
                    remainingTime = Math.max(0, estimatedTotalTime - elapsed);
                } else {
                    // Use initial estimate
                    remainingTime = tracker.totalReadingTime - elapsed;
                }
                
                elements.timeRemaining.textContent = this.formatDuration(Math.round(remainingTime));
            }
        };
        
        // Update every 30 seconds
        tracker.updateTimer = setInterval(updateTimeDisplay, 30000);
        updateTimeDisplay(); // Initial update
    }

    updateReadingState(tracker, progress) {
        const { elements, indicator } = tracker;
        
        // Remove previous state classes
        const stateClasses = ['reading-state-starting', 'reading-state-progress', 'reading-state-halfway', 'reading-state-almost', 'reading-state-complete'];
        indicator.classList.remove(...stateClasses);
        
        // Add current state class and update motivation
        let stateClass, motivationText;
        
        if (progress >= 95) {
            stateClass = 'reading-state-complete';
            motivationText = this.getMotivationMessage(progress, 'complete');
            indicator.classList.add('progress-completed');
        } else if (progress >= 80) {
            stateClass = 'reading-state-almost';
            motivationText = this.getMotivationMessage(progress, 'almost');
            indicator.classList.add('reading-active');
        } else if (progress >= 45) {
            stateClass = 'reading-state-halfway';
            motivationText = this.getMotivationMessage(progress, 'halfway');
            indicator.classList.add('reading-active');
        } else if (progress >= 10) {
            stateClass = 'reading-state-progress';
            motivationText = this.getMotivationMessage(progress, 'progress');
            indicator.classList.add('reading-active');
        } else {
            stateClass = 'reading-state-starting';
            motivationText = this.getMotivationMessage(progress, 'starting');
        }
        
        indicator.classList.add(stateClass);
        
        // Update motivation message
        if (elements.motivationMessage) {
            elements.motivationMessage.textContent = motivationText;
        }
    }

    getMotivationMessage(progress, stage) {
        const messages = {
            starting: [
                "Let's dive in! 🚀",
                "Ready to learn! 📚",
                "Adventure begins! 🗺️",
                "Time to explore! 🔍"
            ],
            progress: [
                "Great start! 🌱",
                "Making progress! 📈",
                "You're doing great! ⭐",
                "Keep it up! 💪"
            ],
            halfway: [
                "Halfway there! 🎯",
                "Excellent progress! 🔥",
                "You're crushing it! 💫",
                "Outstanding work! 🌟"
            ],
            almost: [
                "Almost there! ⚡",
                "Final stretch! 🏁",
                "You're so close! 🎊",
                "Nearly done! 🚀"
            ],
            complete: [
                "Fantastic work! 🎉",
                "Mission complete! ✅",
                "You did it! 🏆",
                "Excellent job! 💎"
            ]
        };
        
        const stageMessages = messages[stage] || messages.starting;
        return stageMessages[Math.floor(Math.random() * stageMessages.length)];
    }

    formatDuration(minutes) {
        if (minutes < 1) return "< 1min";
        if (minutes < 60) return `${minutes}min`;
        
        const hours = Math.floor(minutes / 60);
        const remainingMinutes = minutes % 60;
        
        if (remainingMinutes === 0) return `${hours}h`;
        return `${hours}h ${remainingMinutes}m`;
    }

    formatNumber(num) {
        if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
        if (num >= 1000) return `${(num / 1000).toFixed(1)}k`;
        return num.toString();
    }
    
    // ========== RESPONSIVE BEHAVIOR ========== //
    
    initializeResponsiveBehavior() {
        console.log('📱 Initializing responsive behavior...');
        
        const resizeHandler = this.debounce(this.handleResize, 250);
        window.addEventListener('resize', resizeHandler);
        this.timers.add(() => window.removeEventListener('resize', resizeHandler));
        
        this.initializeTouchGestures();
        this.initializeResponsiveNavigation();
        
        console.log('✅ Responsive behavior initialized');
    }
    
    handleResize() {
        this.updateScrollButtons();
        this.adjustGridLayouts();
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
        this.timers.add(() => document.removeEventListener('keydown', this.handleKeyboardShortcuts));
        
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
        
        this.initializeParallaxEffects();
        this.initializeScrollToTop();
        
        // Reading progress (unified for all pages)
        this.initializeReadingProgress();
        
        console.log('✅ Scroll effects initialized');
    }
    
    initializeParallaxEffects() {
        const parallaxElements = document.querySelectorAll('.terminal-window, .featured-datalog-container');
        
        const parallaxHandler = this.throttle(() => {
            const scrolled = window.pageYOffset;
            
            parallaxElements.forEach(element => {
                const rate = scrolled * -0.1;
                element.style.transform = `translateY(${rate}px)`;
            });
        }, 16);
        
        window.addEventListener('scroll', parallaxHandler);
        this.timers.add(() => window.removeEventListener('scroll', parallaxHandler));
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
        
        const scrollHandler = this.throttle(() => {
            if (window.pageYOffset > 300) {
                scrollToTopBtn.style.opacity = '1';
                scrollToTopBtn.style.visibility = 'visible';
            } else {
                scrollToTopBtn.style.opacity = '0';
                scrollToTopBtn.style.visibility = 'hidden';
            }
        }, 100);
        
        window.addEventListener('scroll', scrollHandler);
        this.timers.add(() => window.removeEventListener('scroll', scrollHandler));
    }
    
    // ========== PERFORMANCE OPTIMIZATIONS ========== //
    
    initializePerformanceOptimizations() {
        console.log('⚡ Initializing performance optimizations...');
        
        this.initializeLazyLoading();
        this.optimizeIntersectionObservers();
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
            this.observers.add(imageObserver);
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
        this.observers.add(cardObserver);
    }
    
    initializeMemoryManagement() {
        const beforeUnloadHandler = () => {
            this.cleanup();
        };
        
        window.addEventListener('beforeunload', beforeUnloadHandler);
        this.timers.add(() => window.removeEventListener('beforeunload', beforeUnloadHandler));
        
        const cacheCleanupInterval = setInterval(() => {
            this.cleanupCache();
        }, 300000);
        this.timers.add(() => clearInterval(cacheCleanupInterval));
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
        const clickHandler = (e) => {
            if (!e.target.closest('.search-suggestions, .filter-panel, .search-panel')) {
                if (this.components.search?.suggestions) {
                    this.hideSearchSuggestions();
                }
            }
        };
        
        document.addEventListener('click', clickHandler);
        this.timers.add(() => document.removeEventListener('click', clickHandler));
        
        const popstateHandler = () => {
            this.loadUserPreferences();
        };
        
        window.addEventListener('popstate', popstateHandler);
        this.timers.add(() => window.removeEventListener('popstate', popstateHandler));
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
                func.call(this, ...args);
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
        console.log('🧹 DataLogs interface cleaning up...');
        
        // Clear all timers
        this.timers.forEach(clearFn => {
            try {
                clearFn();
            } catch (e) {
                // Silently handle cleanup errors
            }
        });
        this.timers.clear();
        
        // Disconnect all observers
        this.observers.forEach(observer => {
            try {
                observer.disconnect();
            } catch (e) {
                // Silently handle cleanup errors
            }
        });
        this.observers.clear();
        
        // Clear component references
        this.components = {};

        // Clean up progress trackers
        if (this.components.progressTrackers) {
            this.components.progressTrackers.forEach(tracker => {
                if (tracker.updateTimer) {
                    clearInterval(tracker.updateTimer);
                }
            });
            this.components.progressTrackers = [];
        }
        
        console.log('✅ DataLogs interface cleaned up');
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

/* TOC Styles */
.toc-link {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    padding: var(--spacing-xs) var(--spacing-sm);
    text-decoration: none;
    color: var(--color-text-secondary);
    border-left: 2px solid transparent;
    transition: all var(--transition-fast);
    font-size: 0.9rem;
    line-height: 1.4;
}

.toc-link:hover {
    color: var(--color-lavender);
    border-left-color: var(--color-lavender);
    background: rgba(179, 157, 219, 0.05);
}

.toc-link.active {
    color: var(--color-lavender);
    border-left-color: var(--color-lavender);
    background: rgba(179, 157, 219, 0.1);
    font-weight: 600;
}

.toc-marker {
    color: var(--color-lavender);
    font-family: var(--font-code);
    font-size: 0.8rem;
    min-width: 20px;
}

.toc-text {
    flex: 1;
}

.toc-level-1 { margin-left: 0; }
.toc-level-2 { margin-left: var(--spacing-sm); }
.toc-level-3 { margin-left: var(--spacing-md); }
.toc-level-4 { margin-left: var(--spacing-lg); }
.toc-level-5 { margin-left: calc(var(--spacing-lg) + var(--spacing-sm)); }
.toc-level-6 { margin-left: calc(var(--spacing-lg) + var(--spacing-md)); }

.toc-empty {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-md);
    color: var(--color-text-tertiary);
    font-style: italic;
    font-size: 0.9rem;
}

.toc-loading {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-md);
    color: var(--color-text-secondary);
    font-size: 0.9rem;
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

// Support for older browsers that don't have Set/Map
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

// Post detail specific functions
window.generateTableOfContents = function() {
    if (window.datalogInterface && window.datalogInterface.generateTableOfContents) {
        window.datalogInterface.generateTableOfContents();
    }
};

window.updateReadingProgress = function() {
    if (window.datalogInterface && window.datalogInterface.initializeReadingProgress) {
        window.datalogInterface.initializeReadingProgress();
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

window.updateReadingProgress = function() {
    if (window.datalogInterface && window.datalogInterface.components.progressTrackers) {
        window.datalogInterface.components.progressTrackers.forEach(tracker => {
            window.datalogInterface.updateProgress(tracker);
        });
    }
};

window.resetReadingProgress = function() {
    if (window.datalogInterface && window.datalogInterface.components.progressTrackers) {
        window.datalogInterface.components.progressTrackers.forEach(tracker => {
            tracker.startTime = Date.now();
            tracker.lastProgress = 0;
            window.datalogInterface.updateProgressDisplay(tracker, 0);
        });
    }
};

// ========== PERFORMANCE MONITORING ========== //

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

// ========== MODULE EXPORTS ========== //

if (typeof module !== 'undefined' && module.exports) {
    module.exports = DatalogInterface;
}

if (typeof define === 'function' && define.amd) {
    define(function() {
        return DatalogInterface;
    });
}

console.log('🚀 DataLogs consolidated JavaScript loaded successfully');
console.log('📋 Available functions: initDatalogsInterface(), updateCategoryScroll(), focusDatalogSearch(), toggleDatalogFilters()');
console.log('📖 Post detail functions: generateTableOfContents(), updateReadingProgress()');
console.log('🐛 Debug functions: enableDatalogDebug(), disableDatalogDebug(), getDatalogState()');
console.log('💫 Interface ready with enhanced performance and memory management');
        