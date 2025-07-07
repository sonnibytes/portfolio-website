// ================================
// 1. GITHUB INTEGRATION JAVASCRIPT
// ================================
// projects/static/projects/js/github-integration.js

class GitHubIntegration {
    constructor(options = {}) {
        this.options = {
            syncUrl: options.syncUrl || '/projects/github/sync/',
            csrfToken: options.csrfToken || '',
            updateInterval: options.updateInterval || 30000, // 30 seconds
            ...options
        };
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.startPeriodicUpdates();
        this.initializeAnimations();
    }
    
    bindEvents() {
        // Sync button event listeners
        const syncButton = document.getElementById('sync-github-data');
        const forceSyncButton = document.getElementById('force-sync');
        
        if (syncButton) {
            syncButton.addEventListener('click', () => this.syncGitHubData(false));
        }
        
        if (forceSyncButton) {
            forceSyncButton.addEventListener('click', () => this.syncGitHubData(true));
        }
        
        // Repository card interactions
        this.initRepositoryCards();
    }
    
    initRepositoryCards() {
        const repoCards = document.querySelectorAll('.repository-card');
        
        repoCards.forEach(card => {
            // Add hover effects
            card.addEventListener('mouseenter', () => {
                this.animateCard(card, 'hover');
            });
            
            card.addEventListener('mouseleave', () => {
                this.animateCard(card, 'unhover');
            });
            
            // Language bar animations
            const langBars = card.querySelectorAll('.lang-bar');
            if (langBars.length > 0) {
                this.animateLanguageBars(langBars);
            }
        });
    }
    
    animateCard(card, action) {
        if (action === 'hover') {
            card.style.transform = 'translateY(-8px) scale(1.02)';
            card.style.boxShadow = '0 12px 30px rgba(179, 157, 219, 0.4)';
        } else {
            card.style.transform = 'translateY(0) scale(1)';
            card.style.boxShadow = '';
        }
    }
    
    animateLanguageBars(bars) {
        bars.forEach((bar, index) => {
            // Animate language bars on scroll into view
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        setTimeout(() => {
                            bar.style.transform = 'scaleX(1)';
                            bar.style.opacity = '1';
                        }, index * 100);
                    }
                });
            });
            
            // Initial state
            bar.style.transform = 'scaleX(0)';
            bar.style.opacity = '0';
            bar.style.transformOrigin = 'left';
            bar.style.transition = 'all 0.6s ease';
            
            observer.observe(bar);
        });
    }
    
    async syncGitHubData(force = false) {
        const statusElement = document.getElementById('sync-status');
        const syncButton = document.getElementById('sync-github-data');
        const forceSyncButton = document.getElementById('force-sync');
        
        // Update UI to show loading state
        this.updateSyncStatus('loading', 'Synchronizing GitHub data...');
        
        if (syncButton) syncButton.disabled = true;
        if (forceSyncButton) forceSyncButton.disabled = true;
        
        try {
            const response = await fetch(this.options.syncUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.options.csrfToken
                },
                body: JSON.stringify({ force: force })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.updateSyncStatus('success', data.message || 'Sync completed successfully');
                this.updateLastSyncTime();
                
                // Optionally reload page or update data
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                throw new Error(data.error || 'Sync failed');
            }
            
        } catch (error) {
            console.error('GitHub sync error:', error);
            this.updateSyncStatus('error', `Sync failed: ${error.message}`);
        } finally {
            // Re-enable buttons
            if (syncButton) syncButton.disabled = false;
            if (forceSyncButton) forceSyncButton.disabled = false;
        }
    }
    
    updateSyncStatus(type, message) {
        const statusElement = document.getElementById('sync-status');
        if (statusElement) {
            statusElement.className = `sync-status ${type}`;
            statusElement.textContent = message;
        }
    }
    
    updateLastSyncTime() {
        const lastSyncElement = document.getElementById('last-sync-time');
        if (lastSyncElement) {
            const now = new Date();
            lastSyncElement.textContent = now.toLocaleString();
        }
    }
    
    startPeriodicUpdates() {
        // Check for new activity periodically
        setInterval(() => {
            this.checkForUpdates();
        }, this.options.updateInterval);
    }
    
    async checkForUpdates() {
        // Lightweight check for updates without full sync
        try {
            const response = await fetch(`${this.options.syncUrl}?check_only=true`);
            const data = await response.json();
            
            if (data.has_updates) {
                this.showUpdateNotification();
            }
        } catch (error) {
            console.warn('Update check failed:', error);
        }
    }
    
    showUpdateNotification() {
        // Show subtle notification about available updates
        const notification = document.createElement('div');
        notification.className = 'update-notification';
        notification.innerHTML = `
            <i class="fas fa-info-circle"></i>
            New GitHub activity detected
            <button onclick="window.location.reload()">Refresh</button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    initializeAnimations() {
        // Animate metrics on page load
        this.animateMetrics();
        this.animateProgressBars();
    }
    
    animateMetrics() {
        const metricValues = document.querySelectorAll('.metric-value');
        
        metricValues.forEach(element => {
            const finalValue = element.textContent;
            const numericValue = parseInt(finalValue.replace(/[^\d]/g, ''));
            
            if (numericValue && numericValue > 0) {
                let currentValue = 0;
                const increment = Math.ceil(numericValue / 30);
                
                const counter = setInterval(() => {
                    currentValue += increment;
                    if (currentValue >= numericValue) {
                        currentValue = numericValue;
                        clearInterval(counter);
                    }
                    
                    element.textContent = finalValue.replace(/\d+/, currentValue.toString());
                }, 50);
            }
        });
    }
    
    animateProgressBars() {
        const progressBars = document.querySelectorAll('.progress-fill');
        
        progressBars.forEach(bar => {
            const targetWidth = bar.style.width;
            bar.style.width = '0%';
            
            setTimeout(() => {
                bar.style.width = targetWidth;
            }, 500);
        });
    }
}