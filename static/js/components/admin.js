// static/js/components/admin.js
/**
 * AURA Portfolio Admin Interface JavaScript
 * Enhanced admin functionality with AURA theme integration
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
    
    // Enhanced table functionality
    initTableFeatures() {
        this.initSortableColumns();
        this.initRowSelection();
        this.initQuickSearch();
        this.initRowActions();
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
        const searchInput = document.querySelector('input[name="search"]');
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
                    this.confirmDelete(button.href);
                }
            });
        });
    }
    
    confirmDelete(deleteUrl) {
        if (confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
            window.location.href = deleteUrl;
        }
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
        
        notification.className = `alert alert-${type} alert-dismissible fade show mb-2`;
        notification.innerHTML = `
            <i class="${icons[type]} me-2"></i>
            ${message}
            <button type="button" class="btn-close" onclick="this.parentNode.remove()"></button>
        `;
        
        container.appendChild(notification);
        
        // Auto-hide after duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
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

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AURAAdmin;
}