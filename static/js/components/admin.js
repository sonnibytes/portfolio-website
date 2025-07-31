// static/js/components/admin.js
/**
 * AURA Portfolio Admin Interface JavaScript
 * Enhanced admin functionality with AURA theme integration
 * Includes DataLog-specific features for category and tag management
 * Version 3.0 - With updates for DataLogs Pages
 */

class AURAAdmin {
    constructor() {
        this.init();
    }
    
    init() {
        console.log('🛡️ AURA Admin Interface Initializing...');
        
        this.initFormEnhancements();
        this.initTableFeatures();
        this.initNotifications();
        this.initKeyboardShortcuts();
        this.initAjaxForms();
        this.initThemeFeatures();
        
        // DataLog-specific features
        this.initDataLogFeatures();
        
        console.log('✅ AURA Admin Interface Ready');
    }
    
    // Enhanced form functionality
    initFormEnhancements() {
        // Auto-resize textareas
        const textareas = document.querySelectorAll('textarea');
        textareas.forEach(textarea => {
            this.autoResizeTextarea(textarea);
            textarea.addEventListener('input', () => this.autoResizeTextarea(textarea));
        });
        
        // Enhanced file input previews
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            if (input.accept && input.accept.includes('image')) {
                this.initImagePreview(input);
            }
        });
        
        // Smart slug generation
        this.initSlugGeneration();
        
        // Form validation enhancements
        this.initFormValidation();
        
        // Markdown preview for MarkdownX fields
        this.initMarkdownPreviews();
        
        // DataLog-specific form enhancements
        this.initAutoSubmitFilters();
        this.initSearchDebounce();
    }
    
    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    }
    
    initImagePreview(input) {
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    let preview = input.parentNode.querySelector('.image-preview');
                    if (!preview) {
                        preview = document.createElement('div');
                        preview.className = 'image-preview mt-2';
                        input.parentNode.appendChild(preview);
                    }
                    
                    preview.innerHTML = `
                        <img src="${e.target.result}" 
                             alt="Preview" 
                             style="max-width: 200px; max-height: 200px; object-fit: cover; border-radius: 0.5rem; border: 1px solid rgba(255,255,255,0.2);">
                        <button type="button" class="btn btn-sm btn-outline-danger mt-1" onclick="this.parentNode.remove(); this.parentNode.parentNode.querySelector('input').value = '';">
                            <i class="fas fa-times"></i> Remove
                        </button>
                    `;
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    initSlugGeneration() {
        const titleFields = document.querySelectorAll('input[name="title"], input[name="name"]');
        const slugFields = document.querySelectorAll('input[name="slug"]');
        
        titleFields.forEach((titleField, index) => {
            const slugField = slugFields[index];
            if (slugField && !slugField.value) {
                titleField.addEventListener('input', () => {
                    if (!slugField.dataset.modified) {
                        slugField.value = this.generateSlug(titleField.value);
                    }
                });
                
                slugField.addEventListener('input', () => {
                    slugField.dataset.modified = 'true';
                });
            }
        });
    }
    
    generateSlug(text) {
        return text
            .toLowerCase()
            .replace(/[^\w\s-]/g, '')
            .replace(/[\s_-]+/g, '-')
            .replace(/^-+|-+$/g, '');
    }
    
    initFormValidation() {
        const forms = document.querySelectorAll('form.admin-form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    this.showValidationErrors(form);
                }
            });
        });
    }
    
    validateForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');
            } else {
                field.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    }
    
    showValidationErrors(form) {
        const invalidFields = form.querySelectorAll('.is-invalid');
        if (invalidFields.length > 0) {
            invalidFields[0].focus();
            this.showNotification('Please fill in all required fields.', 'error');
        }
    }
    
    initMarkdownPreviews() {
        const markdownFields = document.querySelectorAll('.markdownx-editor');
        markdownFields.forEach(field => {
            const previewButton = document.createElement('button');
            previewButton.type = 'button';
            previewButton.className = 'btn btn-sm btn-outline-secondary mt-2';
            previewButton.innerHTML = '<i class="fas fa-eye"></i> Preview';
            
            previewButton.addEventListener('click', () => {
                this.toggleMarkdownPreview(field);
            });
            
            field.parentNode.appendChild(previewButton);
        });
    }
    
    toggleMarkdownPreview(field) {
        let preview = field.parentNode.querySelector('.markdown-preview');
        
        if (preview) {
            preview.remove();
        } else {
            preview = document.createElement('div');
            preview.className = 'markdown-preview mt-3 p-3';
            preview.style.cssText = `
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 0.5rem;
                max-height: 300px;
                overflow-y: auto;
            `;
            
            // Convert markdown to HTML (basic implementation)
            const markdown = field.value;
            preview.innerHTML = this.simpleMarkdownToHtml(markdown);
            
            field.parentNode.appendChild(preview);
        }
    }
    
    simpleMarkdownToHtml(markdown) {
        return markdown
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
            .replace(/\*(.*)\*/gim, '<em>$1</em>')
            .replace(/!\[([^\]]*)\]\(([^\)]*)\)/gim, '<img alt="$1" src="$2" style="max-width: 100%;">')
            .replace(/\[([^\]]*)\]\(([^\)]*)\)/gim, '<a href="$2">$1</a>')
            .replace(/\n/gim, '<br>');
    }
    
    // Auto-submit filter forms when selects change (DataLog feature)
    initAutoSubmitFilters() {
        const filterForms = document.querySelectorAll('.filter-form');
        
        filterForms.forEach(form => {
            const selects = form.querySelectorAll('select');
            selects.forEach(select => {
                select.addEventListener('change', () => {
                    form.submit();
                });
            });
        });
    }

    // Debounced search input submission (DataLog feature)
    initSearchDebounce(delay = 500, minLength = 2) {
        const searchInputs = document.querySelectorAll('.filter-form input[name="search"]');
        
        searchInputs.forEach(input => {
            let searchTimeout;
            
            input.addEventListener('input', () => {
                clearTimeout(searchTimeout);
                
                searchTimeout = setTimeout(() => {
                    const value = input.value.trim();
                    if (value.length >= minLength || value.length === 0) {
                        const form = input.closest('form');
                        if (form) {
                            form.submit();
                        }
                    }
                }, delay);
            });
        });
    }
    
    // Enhanced table functionality
    initTableFeatures() {
        this.initSortableColumns();
        this.initRowSelection();
        this.initQuickSearch();
        this.initRowActions();
        this.initTableInteractions(); // DataLog feature
    }
    
    initSortableColumns() {
        const headers = document.querySelectorAll('.admin-table th[data-sort]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                const column = header.dataset.sort;
                const currentOrder = header.dataset.order || 'asc';
                const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
                
                // Update URL with sort parameters
                const url = new URL(window.location);
                url.searchParams.set('sort', column);
                url.searchParams.set('order', newOrder);
                window.location.href = url.toString();
            });
        });
    }
    
    initRowSelection() {
        const selectAllCheckbox = document.getElementById('select-all');
        const rowCheckboxes = document.querySelectorAll('.row-select');
        
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                rowCheckboxes.forEach(checkbox => {
                    checkbox.checked = e.target.checked;
                    this.toggleRowHighlight(checkbox);
                });
                this.updateBulkActionsVisibility();
            });
        }
        
        rowCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.toggleRowHighlight(checkbox);
                this.updateSelectAllState();
                this.updateBulkActionsVisibility();
            });
        });
    }
    
    toggleRowHighlight(checkbox) {
        const row = checkbox.closest('tr');
        if (checkbox.checked) {
            row.classList.add('selected');
        } else {
            row.classList.remove('selected');
        }
    }
    
    updateSelectAllState() {
        const selectAllCheckbox = document.getElementById('select-all');
        const rowCheckboxes = document.querySelectorAll('.row-select');
        const checkedBoxes = document.querySelectorAll('.row-select:checked');
        
        if (selectAllCheckbox) {
            selectAllCheckbox.checked = checkedBoxes.length === rowCheckboxes.length;
            selectAllCheckbox.indeterminate = checkedBoxes.length > 0 && checkedBoxes.length < rowCheckboxes.length;
        }
    }
    
    updateBulkActionsVisibility() {
        const bulkActionsBar = document.querySelector('.bulk-actions-bar');
        const selectedCount = document.querySelectorAll('.row-select:checked').length;
        const countElement = document.querySelector('.selected-count');
        
        if (bulkActionsBar) {
            if (selectedCount > 0) {
                bulkActionsBar.style.display = 'block';
                if (countElement) {
                    countElement.textContent = `${selectedCount} item${selectedCount !== 1 ? 's' : ''} selected`;
                }
            } else {
                bulkActionsBar.style.display = 'none';
            }
        }
    }
    
    initQuickSearch() {
        const searchInput = document.querySelector('input[name="search"]:not(.filter-form input[name="search"])');
        if (searchInput) {
            let searchTimeout;
            
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.performQuickSearch(e.target.value);
                }, 300);
            });
        }
    }
    
    performQuickSearch(query) {
        const rows = document.querySelectorAll('.admin-table tbody tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const matches = text.includes(query.toLowerCase());
            row.style.display = matches ? '' : 'none';
        });
    }
    
    initRowActions() {
        const actionButtons = document.querySelectorAll('.action-buttons .btn');
        actionButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                if (button.href && button.href.includes('delete')) {
                    e.preventDefault();
                    this.confirmDelete(button.href, button);
                }
            });
        });
    }
    
    confirmDelete(deleteUrl, button = null) {
        // Enhanced confirmation with item identification
        let itemName = '';
        let itemType = 'item';
        
        if (button) {
            const container = button.closest('.category-card, .admin-table-row, tr');
            if (container) {
                if (container.classList.contains('category-card')) {
                    itemType = 'category';
                    const nameElement = container.querySelector('.category-details h4');
                    itemName = nameElement?.textContent.trim() || '';
                } else {
                    // Check if it's a tag row
                    const tagElement = container.querySelector('.tag-name');
                    if (tagElement) {
                        itemType = 'tag';
                        itemName = tagElement.textContent.replace('#', '').trim();
                    }
                }
            }
        }
        
        const message = `Are you sure you want to delete this ${itemType}?` +
                      (itemName ? `\n\n"${itemName}" will be permanently removed.` : '') +
                      `\n\nThis action cannot be undone.`;
        
        if (confirm(message)) {
            window.location.href = deleteUrl;
        }
    }
    
    // Enhanced table interactions (DataLog feature)
    initTableInteractions() {
        const tables = document.querySelectorAll('.admin-table');
        
        tables.forEach(table => {
            const rows = table.querySelectorAll('.admin-table-row, tbody tr');
            rows.forEach(row => {
                row.addEventListener('click', (e) => {
                    // Don't highlight if clicking on action buttons or links
                    if (e.target.closest('a, button, input')) return;
                    
                    // Remove previous highlights
                    rows.forEach(r => r.classList.remove('row-highlighted'));
                    
                    // Add highlight to clicked row
                    row.classList.add('row-highlighted');
                });
            });
        });
    }
    
    // Enhanced notifications
    initNotifications() {
        this.createNotificationContainer();
        this.autoHideAlerts();
    }
    
    createNotificationContainer() {
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }
    }
    
    showNotification(message, type = 'info', duration = 5000) {
        const container = document.getElementById('notification-container');
        const notification = document.createElement('div');
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        const backgrounds = {
            success: 'rgba(76, 175, 80, 0.9)',
            error: 'rgba(244, 67, 54, 0.9)',
            warning: 'rgba(255, 152, 0, 0.9)',
            info: 'rgba(179, 157, 219, 0.9)'
        };
        
        notification.className = `alert alert-${type} alert-dismissible fade show mb-2`;
        notification.style.cssText = `
            background: ${backgrounds[type]};
            border: 1px solid rgba(255,255,255,0.2);
            color: white;
            border-radius: 8px;
            padding: 1rem 1.5rem;
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center;">
                <i class="${icons[type]} me-2"></i>
                <span>${message}</span>
                <button type="button" style="background: none; border: none; color: white; margin-left: auto; cursor: pointer;" onclick="this.parentNode.parentNode.remove()">×</button>
            </div>
        `;
        
        container.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Auto-hide after duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 300);
            }
        }, duration);
    }
    
    autoHideAlerts() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(alert => {
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.classList.remove('show');
                    setTimeout(() => alert.remove(), 300);
                }
            }, 5000);
        });
    }
    
    // Keyboard shortcuts
    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + S to save forms
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                const form = document.querySelector('form.admin-form');
                if (form) {
                    form.submit();
                    this.showNotification('Saving...', 'info', 1000);
                }
            }
            
            // Escape to close modals/previews
            if (e.key === 'Escape') {
                const previews = document.querySelectorAll('.markdown-preview');
                previews.forEach(preview => preview.remove());
            }
            
            // Ctrl/Cmd + Enter to submit and continue editing
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                const continueButton = document.querySelector('button[name="save_and_continue"]');
                if (continueButton) {
                    continueButton.click();
                }
            }
        });
    }
    
    // AJAX form handling
    initAjaxForms() {
        const ajaxForms = document.querySelectorAll('form[data-ajax="true"]');
        ajaxForms.forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitFormAjax(form);
            });
        });
    }
    
    async submitFormAjax(form) {
        const formData = new FormData(form);
        const submitButton = form.querySelector('button[type="submit"]');
        
        // Show loading state
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
        submitButton.disabled = true;
        
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification(data.message, 'success');
                if (data.redirect_url) {
                    setTimeout(() => {
                        window.location.href = data.redirect_url;
                    }, 1000);
                }
            } else {
                this.showNotification(data.message, 'error');
                this.displayFormErrors(form, data.errors);
            }
        } catch (error) {
            this.showNotification('An error occurred while saving.', 'error');
            console.error('Form submission error:', error);
        } finally {
            // Restore button state
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
        }
    }
    
    displayFormErrors(form, errors) {
        // Clear existing error displays
        form.querySelectorAll('.field-error').forEach(el => el.remove());
        form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        
        // Display new errors
        for (const [fieldName, fieldErrors] of Object.entries(errors)) {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                field.classList.add('is-invalid');
                
                const errorDiv = document.createElement('div');
                errorDiv.className = 'field-error text-danger mt-1';
                errorDiv.innerHTML = fieldErrors.map(error => 
                    `<small><i class="fas fa-exclamation-circle me-1"></i>${error}</small>`
                ).join('<br>');
                
                field.parentNode.appendChild(errorDiv);
            }
        }
    }
    
    // Theme-specific features
    initThemeFeatures() {
        this.initGlowEffects();
        this.initProgressBars();
        this.initCounterAnimations();
        this.initDataLogAnimations(); // DataLog-specific animations
    }
    
    initGlowEffects() {
        const glowElements = document.querySelectorAll('.btn-admin-primary, .status-badge');
        glowElements.forEach(element => {
            element.addEventListener('mouseenter', () => {
                element.style.boxShadow = '0 0 20px rgba(var(--cyan-rgb), 0.5)';
            });
            
            element.addEventListener('mouseleave', () => {
                element.style.boxShadow = '';
            });
        });
    }
    
    initProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar[data-value]');
        progressBars.forEach(bar => {
            const value = bar.dataset.value;
            bar.style.width = '0%';
            
            setTimeout(() => {
                bar.style.transition = 'width 1s ease-in-out';
                bar.style.width = value + '%';
            }, 100);
        });
    }
    
    initCounterAnimations() {
        const counters = document.querySelectorAll('[data-counter]');
        counters.forEach(counter => {
            const target = parseInt(counter.dataset.counter);
            let current = 0;
            const increment = target / 50;
            
            const updateCounter = () => {
                current += increment;
                if (current < target) {
                    counter.textContent = Math.floor(current);
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = target;
                }
            };
            
            updateCounter();
        });
    }
    
    // DataLog-specific features
    initDataLogFeatures() {
        this.initDataLogAnimations();
        this.initDataLogHoverEffects();
        this.initDataLogUtilities();
    }
    
    // DataLog-specific animations
    initDataLogAnimations() {
        // Animate usage bars and progress indicators
        const usageBars = document.querySelectorAll('.tag-usage-fill');
        usageBars.forEach(bar => {
            const targetWidth = bar.style.width || '0%';
            bar.style.width = '0%';
            
            setTimeout(() => {
                bar.style.transition = 'width 0.8s ease-out';
                bar.style.width = targetWidth;
            }, Math.random() * 500 + 200); // Stagger animations
        });

        // Animate metric counters on stats cards
        const metricCounters = document.querySelectorAll('.text-2xl.font-bold');
        metricCounters.forEach(counter => {
            const target = parseInt(counter.textContent) || 0;
            if (target > 0) {
                const duration = 1000;
                const increment = target / (duration / 16);
                let current = 0;
                
                const updateCounter = () => {
                    current += increment;
                    if (current < target) {
                        counter.textContent = Math.floor(current);
                        requestAnimationFrame(updateCounter);
                    } else {
                        counter.textContent = target;
                    }
                };
                
                setTimeout(updateCounter, 200);
            }
        });
    }
    
    // Enhanced hover effects for DataLog elements
    initDataLogHoverEffects() {
        // Enhanced card hover effects
        const cards = document.querySelectorAll('.category-card, .tag-bubble');
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-4px) scale(1.02)';
                card.style.transition = 'transform 0.3s ease';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) scale(1)';
            });
        });

        // Action button hover effects with rotation
        const actionButtons = document.querySelectorAll('.category-action, .tag-action');
        actionButtons.forEach(button => {
            button.addEventListener('mouseenter', () => {
                button.style.transform = 'scale(1.15) rotate(10deg)';
                button.style.transition = 'transform 0.2s ease';
            });
            
            button.addEventListener('mouseleave', () => {
                button.style.transform = 'scale(1) rotate(0deg)';
            });
        });
    }
    
    // DataLog utility methods
    initDataLogUtilities() {
        // Add global utility methods for DataLog features
        window.DataLogUtils = {
            formatNumber: (num) => num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','),
            randomColor: () => '#' + Math.floor(Math.random()*16777215).toString(16),
            slugify: (text) => text.toString().toLowerCase()
                .replace(/\s+/g, '-')
                .replace(/[^\w\-]+/g, '')
                .replace(/\-\-+/g, '-')
                .replace(/^-+/, '')
                .replace(/-+$/, ''),
            timeAgo: (date) => {
                const now = new Date();
                const diffTime = Math.abs(now - new Date(date));
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                
                if (diffDays === 1) return '1 day ago';
                if (diffDays < 7) return `${diffDays} days ago`;
                if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
                if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
                return `${Math.floor(diffDays / 365)} years ago`;
            }
        };
    }
    
    // Filter management utilities
    clearAllFilters(formSelector = '.filter-form') {
        const form = document.querySelector(formSelector);
        if (!form) return;

        // Clear all inputs
        const inputs = form.querySelectorAll('input[type="text"], input[type="search"]');
        inputs.forEach(input => input.value = '');

        // Reset all selects to first option
        const selects = form.querySelectorAll('select');
        selects.forEach(select => select.selectedIndex = 0);

        // Submit to apply cleared filters
        form.submit();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.auraAdmin = new AURAAdmin();
});

// Global helper functions
function initAdminFeatures() {
    if (window.auraAdmin) {
        window.auraAdmin.init();
    }
}

// Backwards compatibility
window.DataLogAdmin = window.auraAdmin;

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AURAAdmin;
}