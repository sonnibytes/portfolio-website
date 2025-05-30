/**
 * Enhanced DataLogs Post List JavaScript
 * AURA HUD-themed interactive functionality
 * Version: 2.0.0
 */

// Enhanced DataLogs System State
const EnhancedDataLogs = {
    initialized: false,
    searchTimeout: null,
    currentView: 'grid',
    activeFilters: new Set(),
    categoryScrollPosition: 0,
    featuredTerminalActive: false,
    performanceMetrics: {
        loadStartTime: performance.now(),
        interactionCount: 0,
        searchCount: 0,
    }
};

/**
 * Initialize Enhanced DataLogs Interface
 */
function initEnhancedDatalogsInterface() {
    console.log('🚀 Enhanced DataLogs Interface Initializing...');
    
    // Performance tracking
    EnhancedDataLogs.performanceMetrics.loadStartTime = performance.now();
    
    // Initialize all components
    initEnhancedCategories();
    initEnhancedSearch();
    initFeaturedTerminal();
    initViewControls();
    initCardAnimations();
    initFilterSystem();
    initAdvancedInteractions();
    initPerformanceOptimizations();
    initAccessibilityEnhancements();
    initAnalytics();
    
    // Mark as initialized
    EnhancedDataLogs.initialized = true;
    
    const loadTime = performance.now() - EnhancedDataLogs.performanceMetrics.loadStartTime;
    console.log(`✅ Enhanced DataLogs Interface Loaded in ${loadTime.toFixed(2)}ms`);
}

/**
 * Enhanced Categories with Smooth Scrolling and Smart Navigation
 */
function initEnhancedCategories() {
    const scrollContainer = document.getElementById('categoriesGrid');
    const leftBtn = document.getElementById('categoryScrollLeft');
    const rightBtn = document.getElementById('categoryScrollRight');
    
    if (!scrollContainer || !leftBtn || !rightBtn) {
        console.log('📂 Category navigation elements not found, skipping...');
        return;
    }
    
    console.log('📂 Initializing enhanced categories...');
    
    // Enhanced scroll detection with better performance
    function updateScrollButtons() {
        const { scrollLeft, scrollWidth, clientWidth } = scrollContainer;
        const maxScroll = scrollWidth - clientWidth;
        const threshold = 10;
        
        // Left button state
        const canScrollLeft = scrollLeft > threshold;
        leftBtn.style.opacity = canScrollLeft ? '1' : '0.3';
        leftBtn.disabled = !canScrollLeft;
        leftBtn.style.pointerEvents = canScrollLeft ? 'auto' : 'none';
        
        // Right button state
        const canScrollRight = scrollLeft < maxScroll - threshold;
        rightBtn.style.opacity = canScrollRight ? '1' : '0.3';
        rightBtn.disabled = !canScrollRight;
        rightBtn.style.pointerEvents = canScrollRight ? 'auto' : 'none';
        
        // Store current position
        EnhancedDataLogs.categoryScrollPosition = scrollLeft;
    }
    
    // Smart scroll function with easing
    function smoothScroll(direction, customAmount = null) {
        const itemWidth = 140; // Approximate item width + gap
        const scrollAmount = customAmount || itemWidth * 2;
        const currentScroll = scrollContainer.scrollLeft;
        
        let targetScroll;
        if (direction === 'left') {
            targetScroll = Math.max(0, currentScroll - scrollAmount);
        } else {
            const maxScroll = scrollContainer.scrollWidth - scrollContainer.clientWidth;
            targetScroll = Math.min(maxScroll, currentScroll + scrollAmount);
        }
        
        scrollContainer.scrollTo({ 
            left: targetScroll, 
            behavior: 'smooth' 
        });
        
        // Haptic feedback if available
        if ('vibrate' in navigator) {
            navigator.vibrate(50);
        }
    }
    
    // Event listeners with enhanced feedback
    leftBtn.addEventListener('click', function() {
        if (!this.disabled) {
            smoothScroll('left');
            this.classList.add('btn-pressed');
            setTimeout(() => this.classList.remove('btn-pressed'), 150);
        }
    });
    
    rightBtn.addEventListener('click', function() {
        if (!this.disabled) {
            smoothScroll('right');
            this.classList.add('btn-pressed');
            setTimeout(() => this.classList.remove('btn-pressed'), 150);
        }
    });
    
    // Enhanced scroll listener with throttling
    scrollContainer.addEventListener('scroll', throttle(updateScrollButtons, 100));
    
    // Keyboard navigation support
    scrollContainer.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowLeft') {
            e.preventDefault();
            smoothScroll('left', 100);
        } else if (e.key === 'ArrowRight') {
            e.preventDefault();
            smoothScroll('right', 100);
        }
    });
    
    // Touch/swipe support with momentum
    let touchStartX = 0;
    let touchStartTime = 0;
    let scrollStartLeft = 0;
    let isTouch = false;
    
    scrollContainer.addEventListener('touchstart', function(e) {
        isTouch = true;
        touchStartX = e.touches[0].pageX;
        touchStartTime = Date.now();
        scrollStartLeft = scrollContainer.scrollLeft;
        scrollContainer.style.scrollBehavior = 'auto';
    }, { passive: true });
    
    scrollContainer.addEventListener('touchmove', function(e) {
        if (!isTouch) return;
        
        const x = e.touches[0].pageX;
        const walk = (touchStartX - x) * 1.5; // Sensitivity multiplier
        scrollContainer.scrollLeft = scrollStartLeft + walk;
    }, { passive: true });
    
    scrollContainer.addEventListener('touchend', function(e) {
        if (!isTouch) return;
        
        const touchEndTime = Date.now();
        const touchDuration = touchEndTime - touchStartTime;
        const touchEndX = e.changedTouches[0].pageX;
        const touchDistance = Math.abs(touchEndX - touchStartX);
        
        // Add momentum for quick swipes
        if (touchDuration < 300 && touchDistance > 50) {
            const velocity = touchDistance / touchDuration;
            const momentum = Math.min(velocity * 100, 300);
            const direction = touchEndX < touchStartX ? 'right' : 'left';
            smoothScroll(direction, momentum);
        }
        
        isTouch = false;
        scrollContainer.style.scrollBehavior = 'smooth';
    }, { passive: true });
    
    // Initialize button states with animation
    setTimeout(() => {
        updateScrollButtons();
        animateCategoriesEntrance();
    }, 100);
    
    // Enhanced category item interactions
    const categoryItems = document.querySelectorAll('.category-item');
    categoryItems.forEach((item, index) => {
        // Enhanced click handling
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active from all categories
            categoryItems.forEach(cat => cat.classList.remove('active'));
            
            // Add active to clicked category
            this.classList.add('active');
            
            // Enhanced click animation
            const hexagon = this.querySelector('.category-hexagon');
            const glow = this.querySelector('.category-glow-effect');
            
            if (hexagon) {
                hexagon.style.transform = 'scale(0.9)';
                setTimeout(() => {
                    hexagon.style.transform = 'scale(1.05)';
                    setTimeout(() => {
                        hexagon.style.transform = 'scale(1)';
                    }, 150);
                }, 100);
            }
            
            if (glow) {
                glow.style.opacity = '1';
                glow.style.transform = 'translate(-50%, -50%) scale(1.5)';
                setTimeout(() => {
                    glow.style.opacity = '0.4';
                    glow.style.transform = 'translate(-50%, -50%) scale(1)';
                }, 300);
            }
            
            // Navigate after animation
            setTimeout(() => {
                window.location.href = this.href;
            }, 200);
        });
        
        // Enhanced hover effects
        item.addEventListener('mouseenter', function() {
            const glowEffect = this.querySelector('.category-glow-effect');
            const hexagon = this.querySelector('.category-hexagon');
            
            if (glowEffect) {
                glowEffect.style.opacity = '0.8';
                glowEffect.style.transform = 'translate(-50%, -50%) scale(1.2)';
            }
            if (hexagon) {
                hexagon.style.transform = 'scale(1.05)';
            }
        });
        
        item.addEventListener('mouseleave', function() {
            if (!this.classList.contains('active')) {
                const glowEffect = this.querySelector('.category-glow-effect');
                const hexagon = this.querySelector('.category-hexagon');
                
                if (glowEffect) {
                    glowEffect.style.opacity = '0.4';
                    glowEffect.style.transform = 'translate(-50%, -50%) scale(1)';
                }
                if (hexagon) {
                    hexagon.style.transform = 'scale(1)';
                }
            }
        });
    });
    
    // Window resize handler
    window.addEventListener('resize', throttle(updateScrollButtons, 150));
    
    console.log('✅ Enhanced categories initialized');
}

/**
 * Animate Categories Entrance
 */
function animateCategoriesEntrance() {
    const categoryItems = document.querySelectorAll('.category-item');
    
    categoryItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(20px) scale(0.9)';
        item.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        
        setTimeout(() => {
            item.style.opacity = '1';
            item.style.transform = 'translateY(0) scale(1)';
        }, 100 + (index * 50));
    });
}

/**
 * Enhanced Search with Real-time Suggestions and Analytics
 */
function initEnhancedSearch() {
    const searchInput = document.querySelector('.search-main-input input');
    const suggestions = document.getElementById('searchSuggestions');
    const suggestionsList = document.getElementById('suggestionsList');
    const searchForm = document.querySelector('.search-form-enhanced');
    
    if (!searchInput) {
        console.log('🔍 Search input not found, skipping...');
        return;
    }
    
    console.log('🔍 Initializing enhanced search...');
    
    // Enhanced search state
    let searchHistory = JSON.parse(localStorage.getItem('aura_search_history') || '[]');
    let currentSuggestionIndex = -1;
    
    // Real-time search with debouncing
    searchInput.addEventListener('input', function() {
        clearTimeout(EnhancedDataLogs.searchTimeout);
        const query = this.value.trim();
        
        if (query.length >= 2) {
            EnhancedDataLogs.searchTimeout = setTimeout(() => {
                loadSearchSuggestions(query);
                trackSearchInteraction('type', query);
            }, 300);
        } else {
            hideSuggestions();
        }
        
        // Reset suggestion index
        currentSuggestionIndex = -1;
    });
    
    // Enhanced keyboard navigation
    searchInput.addEventListener('keydown', function(e) {
        const suggestionItems = document.querySelectorAll('.suggestion-item');
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                currentSuggestionIndex = Math.min(currentSuggestionIndex + 1, suggestionItems.length - 1);
                updateSuggestionHighlight(suggestionItems);
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                currentSuggestionIndex = Math.max(currentSuggestionIndex - 1, -1);
                updateSuggestionHighlight(suggestionItems);
                break;
                
            case 'Enter':
                if (currentSuggestionIndex >= 0 && suggestionItems[currentSuggestionIndex]) {
                    e.preventDefault();
                    suggestionItems[currentSuggestionIndex].click();
                } else if (this.value.trim()) {
                    trackSearchInteraction('submit', this.value.trim());
                    addToSearchHistory(this.value.trim());
                }
                break;
                
            case 'Escape':
                hideSuggestions();
                this.blur();
                break;
        }
    });
    
    // Enhanced focus effects
    searchInput.addEventListener('focus', function() {
        this.closest('.search-main-input').classList.add('search-focused');
        
        if (this.value.length >= 2) {
            loadSearchSuggestions(this.value);
        } else if (searchHistory.length > 0) {
            showSearchHistory();
        }
    });
    
    searchInput.addEventListener('blur', function() {
        this.closest('.search-main-input').classList.remove('search-focused');
        // Delay hiding suggestions to allow for clicks
        setTimeout(hideSuggestions, 150);
    });
    
    // Enhanced suggestion loading
    function loadSearchSuggestions(query) {
        if (!suggestionsList) return;
        
        // Mock API call - replace with actual endpoint
        const mockSuggestions = generateMockSuggestions(query);
        
        if (mockSuggestions.length > 0) {
            const suggestionsHTML = mockSuggestions.map((item, index) => 
                `<div class="suggestion-item" data-index="${index}" onclick="selectSuggestion('${escapeHtml(item.text)}', '${item.type}', '${item.url || ''}')">
                    <i class="${item.icon}"></i>
                    <span class="suggestion-text">${highlightQuery(item.text, query)}</span>
                    <span class="suggestion-type">${item.type}</span>
                </div>`
            ).join('');
            
            suggestionsList.innerHTML = suggestionsHTML;
            showSuggestions();
        } else {
            showNoResults(query);
        }
    }
    
    function generateMockSuggestions(query) {
        const allSuggestions = [
            { text: 'Machine Learning Fundamentals', type: 'post', icon: 'fas fa-brain', url: '/blog/ml-fundamentals/' },
            { text: 'Python Data Analysis', type: 'post', icon: 'fab fa-python', url: '/blog/python-analysis/' },
            { text: 'Django Best Practices', type: 'post', icon: 'fas fa-code', url: '/blog/django-practices/' },
            { text: 'Neural Networks Deep Dive', type: 'post', icon: 'fas fa-project-diagram', url: '/blog/neural-networks/' },
            { text: 'API Development Guide', type: 'category', icon: 'fas fa-plug', url: '/blog/category/api/' },
            { text: 'Database Optimization', type: 'category', icon: 'fas fa-database', url: '/blog/category/database/' },
            { text: 'Machine Learning', type: 'category', icon: 'fas fa-brain', url: '/blog/category/ml/' },
            { text: '#python', type: 'tag', icon: 'fas fa-tag', url: '/blog/tag/python/' },
            { text: '#django', type: 'tag', icon: 'fas fa-tag', url: '/blog/tag/django/' },
            { text: '#ai', type: 'tag', icon: 'fas fa-tag', url: '/blog/tag/ai/' },
            { text: 'System Architecture Patterns', type: 'post', icon: 'fas fa-sitemap', url: '/blog/architecture-patterns/' },
            { text: 'Data Visualization with D3', type: 'post', icon: 'fas fa-chart-line', url: '/blog/d3-visualization/' }
        ];
        
        return allSuggestions.filter(item => 
            item.text.toLowerCase().includes(query.toLowerCase())
        ).slice(0, 6);
    }
    
    function showSearchHistory() {
        if (!suggestionsList || searchHistory.length === 0) return;
        
        const historyHTML = searchHistory.slice(0, 5).map((term, index) => 
            `<div class="suggestion-item history-item" data-index="${index}" onclick="selectSuggestion('${escapeHtml(term)}', 'history')">
                <i class="fas fa-history"></i>
                <span class="suggestion-text">${escapeHtml(term)}</span>
                <span class="suggestion-type">recent</span>
            </div>`
        ).join('');
        
        suggestionsList.innerHTML = `
            <div class="suggestions-section">
                <div class="suggestions-section-title">Recent Searches</div>
                ${historyHTML}
            </div>
        `;
        
        showSuggestions();
    }
    
    function showNoResults(query) {
        if (!suggestionsList) return;
        
        suggestionsList.innerHTML = `
            <div class="no-suggestions">
                <i class="fas fa-search"></i>
                <span>No suggestions found for "${escapeHtml(query)}"</span>
                <div class="suggestion-tip">Try searching for: Python, Django, Machine Learning</div>
            </div>
        `;
        
        showSuggestions();
    }
    
    function updateSuggestionHighlight(items) {
        items.forEach((item, index) => {
            if (index === currentSuggestionIndex) {
                item.classList.add('suggestion-highlighted');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('suggestion-highlighted');
            }
        });
    }
    
    function highlightQuery(text, query) {
        const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
    
    function showSuggestions() {
        if (suggestions) {
            suggestions.style.display = 'block';
            suggestions.classList.add('suggestions-visible');
        }
    }
    
    function hideSuggestions() {
        if (suggestions) {
            suggestions.style.display = 'none';
            suggestions.classList.remove('suggestions-visible');
        }
        currentSuggestionIndex = -1;
    }
    
    function addToSearchHistory(term) {
        // Remove if already exists
        searchHistory = searchHistory.filter(item => item !== term);
        // Add to beginning
        searchHistory.unshift(term);
        // Keep only last 10
        searchHistory = searchHistory.slice(0, 10);
        // Save to localStorage
        localStorage.setItem('aura_search_history', JSON.stringify(searchHistory));
    }
    
    // Global function for suggestion selection
    window.selectSuggestion = function(suggestion, type, url = '') {
        searchInput.value = suggestion;
        hideSuggestions();
        
        trackSearchInteraction('select', suggestion, type);
        addToSearchHistory(suggestion);
        
        if (url) {
            window.location.href = url;
        } else {
            searchInput.closest('form').submit();
        }
    };
    
    // Close suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !suggestions?.contains(e.target)) {
            hideSuggestions();
        }
    });
    
    console.log('✅ Enhanced search initialized');
}

/**
 * Featured Terminal with Advanced Animations
 */
function initFeaturedTerminal() {
    const terminal = document.querySelector('.terminal-container');
    if (!terminal) {
        console.log('💻 Terminal not found, skipping...');
        return;
    }
    
    console.log('💻 Initializing featured terminal...');
    
    // Enhanced intersection observer for better performance
    const terminalObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !EnhancedDataLogs.featuredTerminalActive) {
                activateTerminal(entry.target);
                EnhancedDataLogs.featuredTerminalActive = true;
                terminalObserver.unobserve(entry.target);
            }
        });
    }, { 
        threshold: 0.3,
        rootMargin: '50px'
    });
    
    terminalObserver.observe(terminal);
    
    function activateTerminal(terminal) {
        terminal.classList.add('terminal-active');
        
        // Enhanced terminal dot animation sequence
        const dots = terminal.querySelectorAll('.terminal-dot');
        const dotSequence = [
            { dot: dots[0], delay: 0, color: 'var(--color-coral)' },
            { dot: dots[1], delay: 200, color: 'var(--color-yellow)' },
            { dot: dots[2], delay: 400, color: 'var(--color-mint)' }
        ];
        
        dotSequence.forEach(({ dot, delay, color }) => {
            if (dot) {
                setTimeout(() => {
                    dot.style.opacity = '1';
                    dot.style.transform = 'scale(1)';
                    dot.style.boxShadow = `0 0 10px ${color}`;
                    
                    // Pulse effect
                    setTimeout(() => {
                        dot.style.animation = 'terminalDotPulse 2s ease-in-out infinite';
                    }, 300);
                }, delay);
            }
        });
        
        // Terminal content typing effect
        const codeContainer = terminal.querySelector('.code-display-container');
        if (codeContainer) {
            setTimeout(() => {
                simulateTyping(codeContainer);
            }, 800);
        }
        
        // Terminal status updates
        const statusIndicator = terminal.querySelector('.status-indicator');
        if (statusIndicator) {
            setTimeout(() => {
                statusIndicator.classList.add('operational');
                statusIndicator.style.animation = 'statusPulse 2s ease-in-out infinite';
            }, 1200);
        }
    }
    
    function simulateTyping(container) {
        const originalContent = container.innerHTML;
        const lines = originalContent.split('\n');
        
        container.innerHTML = '';
        container.classList.add('typing-active');
        
        let currentLine = 0;
        let currentChar = 0;
        
        function typeNextChar() {
            if (currentLine >= lines.length) {
                container.classList.remove('typing-active');
                container.classList.add('typing-complete');
                return;
            }
            
            const line = lines[currentLine];
            if (currentChar >= line.length) {
                container.innerHTML += '\n';
                currentLine++;
                currentChar = 0;
                setTimeout(typeNextChar, 100); // Line break pause
                return;
            }
            
            container.innerHTML += line[currentChar];
            currentChar++;
            
            // Variable typing speed for realism
            const delay = Math.random() * 50 + 30;
            setTimeout(typeNextChar, delay);
        }
        
        typeNextChar();
    }
    
    // Enhanced copy functionality
    const copyButtons = terminal.querySelectorAll('.copy-button');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const codeContent = terminal.querySelector('.code-display-container').textContent;
            
            navigator.clipboard.writeText(codeContent).then(() => {
                // Enhanced copy feedback
                this.classList.add('copy-success');
                const originalText = this.querySelector('span').textContent;
                this.querySelector('span').textContent = 'Copied!';
                this.querySelector('i').className = 'fas fa-check';
                
                setTimeout(() => {
                    this.classList.remove('copy-success');
                    this.querySelector('span').textContent = originalText;
                    this.querySelector('i').className = 'fas fa-copy';
                }, 2000);
                
                // Show terminal response
                showTerminalFeedback('Code copied to clipboard');
            }).catch(() => {
                showTerminalFeedback('Copy failed - please try again', 'error');
            });
        });
    });
    
    function showTerminalFeedback(message, type = 'success') {
        const feedback = document.createElement('div');
        feedback.className = `terminal-feedback terminal-feedback-${type}`;
        feedback.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check' : 'exclamation-triangle'}"></i>
            <span>${message}</span>
        `;
        
        terminal.appendChild(feedback);
        
        setTimeout(() => {
            feedback.style.opacity = '1';
            feedback.style.transform = 'translateY(0)';
        }, 10);
        
        setTimeout(() => {
            feedback.style.opacity = '0';
            feedback.style.transform = 'translateY(-10px)';
            setTimeout(() => feedback.remove(), 300);
        }, 3000);
    }
    
    console.log('✅ Featured terminal initialized');
}

/**
 * Advanced View Controls with Smooth Transitions
 */
function initViewControls() {
    const toggleBtns = document.querySelectorAll('.view-toggle-btn');
    const grid = document.getElementById('datalogsGrid');
    const sortSelect = document.getElementById('sortSelect');
    
    if (!grid) {
        console.log('👁️ View controls grid not found, skipping...');
        return;
    }
    
    console.log('👁️ Initializing view controls...');
    
    // Enhanced view toggle with smooth transitions
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const view = this.dataset.view;
            EnhancedDataLogs.currentView = view;
            
            // Update button states
            toggleBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Enhanced transition effect
            grid.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            grid.style.opacity = '0.3';
            grid.style.transform = 'scale(0.98)';
            
            setTimeout(() => {
                // Update grid layout
                grid.className = `datalogs-grid datalogs-${view}`;
                
                // Animate cards based on view
                animateCardsForView(view);
                
                // Reset grid appearance
                grid.style.opacity = '1';
                grid.style.transform = 'scale(1)';
                
                // Store preference
                localStorage.setItem('aura_preferred_view', view);
                
                trackViewChange(view);
            }, 150);
        });
    });
    
    // Load saved view preference
    const savedView = localStorage.getItem('aura_preferred_view');
    if (savedView) {
        const savedViewBtn = document.querySelector(`[data-view="${savedView}"]`);
        if (savedViewBtn) {
            savedViewBtn.click();
        }
    }
    
    // Enhanced sort functionality
    if (sortSelect) {
        // Load saved sort preference
        const savedSort = localStorage.getItem('aura_preferred_sort');
        if (savedSort) {
            sortSelect.value = savedSort;
        }
        
        sortSelect.addEventListener('change', function() {
            const sortValue = this.value;
            
            // Save preference
            localStorage.setItem('aura_preferred_sort', sortValue);
            
            // Enhanced loading state
            this.disabled = true;
            this.style.opacity = '0.6';
            
            // Add loading indicator
            const loadingIndicator = document.createElement('div');
            loadingIndicator.className = 'sort-loading';
            loadingIndicator.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            this.parentNode.appendChild(loadingIndicator);
            
            // Navigate with sort parameter
            const url = new URL(window.location);
            url.searchParams.set('sort', sortValue);
            url.searchParams.delete('page'); // Reset pagination
            
            trackSortChange(sortValue);
            
            setTimeout(() => {
                window.location.href = url.toString();
            }, 500);
        });
    }
    
    console.log('✅ View controls initialized');
}

function animateCardsForView(view) {
    const cards = document.querySelectorAll('.datalog-entry-card');
    
    cards.forEach((card, index) => {
        card.style.transition = `opacity 0.4s ease ${index * 0.05}s, transform 0.4s ease ${index * 0.05}s`;
        card.style.opacity = '0';
        card.style.transform = view === 'list' ? 'translateX(-20px)' : 'translateY(20px)';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translate(0)';
        }, 100 + (index * 50));
    });
}

/**
 * Enhanced Card Animations with Intersection Observer
 */
function initCardAnimations() {
    const cards = document.querySelectorAll('.datalog-entry-card');
    
    if (cards.length === 0) {
        console.log('🎬 No cards found, skipping animations...');
        return;
    }
    
    console.log('🎬 Initializing card animations...');
    
    // Enhanced intersection observer with better performance
    const cardObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCardEntrance(entry.target);
                cardObserver.unobserve(entry.target);
            }
        });
    }, { 
        threshold: 0.1,
        rootMargin: '50px'
    });
    
    // Setup initial card states and observe
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px) scale(0.95)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        
        // Add staggered delay data
        card.dataset.animationDelay = index * 0.1;
        
        cardObserver.observe(card);
        
        // Enhanced hover interactions
        addCardHoverEffects(card);
    });
    
    function animateCardEntrance(card) {
        const delay = parseFloat(card.dataset.animationDelay) * 1000;
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0) scale(1)';
            
            // Add entrance class for additional effects
            card.classList.add('card-animated');
        }, delay);
    }
    
    function addCardHoverEffects(card) {
        let hoverTimeout;
        
        card.addEventListener('mouseenter', function() {
            clearTimeout(hoverTimeout);
            
            // Enhanced image parallax effect
            const image = this.querySelector('.datalog-image');
            if (image) {
                image.style.transform = 'scale(1.05) translateY(-5px)';
            }
            
            // Glow effect on category indicator
            const categoryIndicator = this.querySelector('.category-mini-indicator');
            if (categoryIndicator) {
                categoryIndicator.style.boxShadow = '0 0 15px var(--category-color)';
            }
            
            // Button animation
            const readBtn = this.querySelector('.read-datalog-btn');
            if (readBtn) {
                readBtn.style.transform = 'translateX(5px)';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            hoverTimeout = setTimeout(() => {
                // Reset effects
                const image = this.querySelector('.datalog-image');
                if (image) {
                    image.style.transform = '';
                }
                
                const categoryIndicator = this.querySelector('.category-mini-indicator');
                if (categoryIndicator) {
                    categoryIndicator.style.boxShadow = '';
                }
                
                const readBtn = this.querySelector('.read-datalog-btn');
                if (readBtn) {
                    readBtn.style.transform = '';
                }
            }, 100);
        });
        
        // Enhanced click feedback
        card.addEventListener('click', function(e) {
            if (e.target.closest('.read-datalog-btn') || e.target.closest('a')) {
                // Add click animation
                this.style.transform = 'scale(0.98)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 150);
            }
        });
    }
    
    console.log('✅ Card animations initialized');
}

/**
 * Advanced Filter System with State Management
 */
function initFilterSystem() {
    const filterTags = document.querySelectorAll('.filter-tag');
    const quickFilters = document.querySelector('.filter-tags-container');
    
    if (filterTags.length === 0) {
        console.log('🔧 No filter tags found, skipping...');
        return;
    }
    
    console.log('🔧 Initializing filter system...');
    
    // Load active filters from URL
    const urlParams = new URLSearchParams(window.location.search);
    const activeFilters = new Set();
    
    filterTags.forEach(tag => {
        const filterType = tag.dataset.filter;
        
        // Check if filter is active based on URL params
        if (urlParams.has(filterType) || urlParams.get('category') === filterType) {
            tag.classList.add('active');
            activeFilters.add(filterType);
        }
        
        // Enhanced click handling
        tag.addEventListener('click', function(e) {
            e.preventDefault();
            
            const isActive = this.classList.contains('active');
            const filterValue = this.dataset.filter;
            
            // Enhanced click animation
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
            
            // Toggle filter state
            if (isActive) {
                this.classList.remove('active');
                activeFilters.delete(filterValue);
                removeFilter(filterValue);
            } else {
                this.classList.add('active');
                activeFilters.add(filterValue);
                addFilter(filterValue, this.href);
            }
            
            // Update URL without page reload for better UX
            updateFiltersInURL();
            
            // Track filter interaction
            trackFilterInteraction(filterValue, !isActive);
        });
        
        // Enhanced hover effects with data preview
        tag.addEventListener('mouseenter', function() {
            if (!this.classList.contains('active')) {
                previewFilterResults(this.dataset.filter);
            }
        });
        
        tag.addEventListener('mouseleave', function() {
            hideFilterPreview();
        });
    });
    
    function addFilter(filterValue, href) {
        // For now, just navigate to the filter URL
        // Later can be enhanced for AJAX filtering
        if (href) {
            setTimeout(() => {
                window.location.href = href;
            }, 200);
        }
    }
    
    function removeFilter(filterValue) {
        // Navigate to base URL without this filter
        const url = new URL(window.location);
        url.searchParams.delete(filterValue);
        
        setTimeout(() => {
            window.location.href = url.toString();
        }, 200);
    }
    
    function updateFiltersInURL() {
        // Update browser history without reload
        const url = new URL(window.location);
        
        // This is a placeholder for future AJAX implementation
        // For now, navigation happens in individual filter handlers
    }
    
    function previewFilterResults(filterValue) {
        // Show preview tooltip with expected results count
        // This would connect to your backend API
        showFilterTooltip(filterValue);
    }
    
    function hideFilterPreview() {
        const tooltip = document.querySelector('.filter-preview-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }
    
    function showFilterTooltip(filterValue) {
        hideFilterPreview(); // Remove existing tooltip
        
        const tooltip = document.createElement('div');
        tooltip.className = 'filter-preview-tooltip';
        tooltip.innerHTML = `
            <div class="tooltip-content">
                <span class="tooltip-text">Filter by ${filterValue}</span>
                <span class="tooltip-count">Loading...</span>
            </div>
        `;
        
        document.body.appendChild(tooltip);
        
        // Position tooltip near cursor
        document.addEventListener('mousemove', positionTooltip);
        
        function positionTooltip(e) {
            tooltip.style.left = e.pageX + 10 + 'px';
            tooltip.style.top = e.pageY - 30 + 'px';
        }
        
        // Simulate loading count (replace with actual API call)
        setTimeout(() => {
            const mockCount = Math.floor(Math.random() * 20) + 1;
            const countElement = tooltip.querySelector('.tooltip-count');
            if (countElement) {
                countElement.textContent = `${mockCount} posts`;
            }
        }, 300);
    }
    
    // Enhanced clear all filters functionality
    const clearAllBtn = document.querySelector('.clear-all-filters');
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', function() {
            filterTags.forEach(tag => tag.classList.remove('active'));
            activeFilters.clear();
            
            const url = new URL(window.location);
            url.search = '';
            window.location.href = url.toString();
        });
    }
    
    console.log('✅ Filter system initialized');
}

/**
 * Advanced Interactions and Features
 */
function initAdvancedInteractions() {
    console.log('⚡ Initializing advanced interactions...');
    
    // Enhanced pagination with keyboard navigation
    initPaginationEnhancements();
    
    // Advanced keyboard shortcuts
    initKeyboardShortcuts();
    
    // Scroll-based animations
    initScrollAnimations();
    
    // Enhanced loading states
    initLoadingStates();
    
    console.log('✅ Advanced interactions initialized');
}

function initPaginationEnhancements() {
    const paginationBtns = document.querySelectorAll('.pagination-nav-btn');
    const paginationInfo = document.querySelector('.pagination-info-section');
    
    paginationBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            // Enhanced loading animation
            this.classList.add('loading');
            this.style.pointerEvents = 'none';
            
            const originalText = this.querySelector('span').textContent;
            this.querySelector('span').textContent = 'Loading...';
            
            // Continue with navigation
        });
    });
    
    // Keyboard navigation for pagination
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey || e.metaKey) {
            if (e.key === 'ArrowLeft') {
                const prevBtn = document.querySelector('.pagination-prev');
                if (prevBtn) {
                    e.preventDefault();
                    prevBtn.click();
                }
            } else if (e.key === 'ArrowRight') {
                const nextBtn = document.querySelector('.pagination-next');
                if (nextBtn) {
                    e.preventDefault();
                    nextBtn.click();
                }
            }
        }
    });
}

function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Don't trigger shortcuts when typing in inputs
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 'k':
                    e.preventDefault();
                    focusSearch();
                    break;
                case 'h':
                    e.preventDefault();
                    navigateToHome();
                    break;
                case '1':
                    e.preventDefault();
                    setViewMode('grid');
                    break;
                case '2':
                    e.preventDefault();
                    setViewMode('list');
                    break;
                case '3':
                    e.preventDefault();
                    setViewMode('timeline');
                    break;
            }
        }
        
        // Single key shortcuts
        switch(e.key) {
            case '/':
                e.preventDefault();
                focusSearch();
                break;
            case 'Escape':
                clearFocus();
                break;
        }
    });
}

function focusSearch() {
    const searchInput = document.querySelector('.search-main-input input');
    if (searchInput) {
        searchInput.focus();
        searchInput.select();
    }
}

function setViewMode(mode) {
    const viewBtn = document.querySelector(`[data-view="${mode}"]`);
    if (viewBtn) {
        viewBtn.click();
    }
}

function clearFocus() {
    document.activeElement.blur();
    hideSuggestions();
}

function initScrollAnimations() {
    // Parallax effect for hero sections
    const heroSections = document.querySelectorAll('.featured-datalog-section');
    
    window.addEventListener('scroll', throttle(function() {
        const scrollY = window.pageYOffset;
        
        heroSections.forEach(section => {
            const rate = scrollY * -0.5;
            section.style.transform = `translateY(${rate}px)`;
        });
    }, 16)); // 60fps
}

function initLoadingStates() {
    // Add loading states to all navigation links
    const navLinks = document.querySelectorAll('a[href^="/blog/"], a[href^="/projects/"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (!this.classList.contains('no-loading')) {
                addLoadingState(this);
            }
        });
    });
}

function addLoadingState(element) {
    element.classList.add('loading-state');
    element.style.pointerEvents = 'none';
    
    const loader = document.createElement('div');
    loader.className = 'inline-loader';
    loader.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    element.appendChild(loader);
}

/**
 * Performance Optimizations
 */
function initPerformanceOptimizations() {
    console.log('🚀 Initializing performance optimizations...');
    
    // Lazy load images with enhanced functionality
    initLazyLoading();
    
    // Preload critical resources
    preloadCriticalResources();
    
    // Monitor performance metrics
    monitorPerformance();
    
    console.log('✅ Performance optimizations initialized');
}

function initLazyLoading() {
    const images = document.querySelectorAll('.datalog-image');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    
                    // Add loading state
                    img.style.opacity = '0.5';
                    img.style.filter = 'blur(5px)';
                    
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        
                        img.onload = function() {
                            this.style.opacity = '1';
                            this.style.filter = 'none';
                            this.style.transition = 'opacity 0.3s ease, filter 0.3s ease';
                        };
                    }
                    
                    imageObserver.unobserve(img);
                }
            });
        }, {
            rootMargin: '100px'
        });
        
        images.forEach(img => {
            if (img.dataset.src) {
                imageObserver.observe(img);
            }
        });
    }
}

function preloadCriticalResources() {
    // Preload next page of results
    const nextPageLink = document.querySelector('.pagination-next');
    if (nextPageLink) {
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = nextPageLink.href;
        document.head.appendChild(link);
    }
    
    // Preload category pages for quick navigation
    const categoryLinks = document.querySelectorAll('.category-item[href]');
    categoryLinks.forEach(link => {
        const prefetchLink = document.createElement('link');
        prefetchLink.rel = 'prefetch';
        prefetchLink.href = link.href;
        document.head.appendChild(prefetchLink);
    });
}

function monitorPerformance() {
    // Track Core Web Vitals
    if ('web-vital' in window) {
        // This would integrate with actual web vitals library
        console.log('📊 Performance monitoring active');
    }
    
    // Track interaction delays
    EnhancedDataLogs.performanceMetrics.totalLoadTime = 
        performance.now() - EnhancedDataLogs.performanceMetrics.loadStartTime;
    
    console.log(`📊 Total initialization time: ${EnhancedDataLogs.performanceMetrics.totalLoadTime.toFixed(2)}ms`);
}

/**
 * Analytics and Tracking Functions
 */
function trackSearchInteraction(type, query, additionalData = null) {
    EnhancedDataLogs.performanceMetrics.searchCount++;
    console.log(`🔍 Search ${type}:`, query, additionalData);
    // Integrate with your analytics platform
}

function trackViewChange(view) {
    console.log(`👁️ View changed to: ${view}`);
    // Integrate with your analytics platform
}

function trackSortChange(sortValue) {
    console.log(`🔄 Sort changed to: ${sortValue}`);
    // Integrate with your analytics platform
}

function trackFilterInteraction(filter, isActive) {
    console.log('Here something is for this');
}