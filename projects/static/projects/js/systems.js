/**
 * Projects JavaScript
 * Interactive functionality for the projects/systems app
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all project components
    initSystemCards();
    initDashboard();
    initFilters();
    initDataVisualizations();
    initTechUsageCharts();
    initRealTimeUpdates();
    initAnimations();
});

// ========== SYSTEM CARDS ========== 
function initSystemCards() {
    const systemCards = document.querySelectorAll('.system-card');
    
    systemCards.forEach(card => {
        // Add hover effect with scanning animation
        card.addEventListener('mouseenter', function() {
            const scanLine = this.querySelector('.scan-line');
            if (scanLine) {
                scanLine.style.animationDuration = '1s';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            const scanLine = this.querySelector('.scan-line');
            if (scanLine) {
                scanLine.style.animationDuration = '4s';
            }
        });
        
        // Progress bar animation on intersection
        const progressBar = card.querySelector('.progress-fill');
        if (progressBar) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const width = progressBar.style.width;
                        progressBar.style.width = '0%';
                        setTimeout(() => {
                            progressBar.style.width = width;
                        }, 100);
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });
            
            observer.observe(card);
        }
    });
}

// ========== DASHBOARD FUNCTIONALITY ==========
function initDashboard() {
    // Metric cards animation
    const metricCards = document.querySelectorAll('.metric-card');
    
    metricCards.forEach((card, index) => {
        // Animate metric values on load
        const metricValue = card.querySelector('.metric-value');
        if (metricValue) {
            const finalValue = metricValue.textContent;
            const numericValue = parseFloat(finalValue.replace(/[^\d.]/g, ''));
            
            if (!isNaN(numericValue)) {
                animateNumber(metricValue, 0, numericValue, 2000, finalValue.replace(/[\d.]/g, ''));
            }
        }
        
        // Stagger card animations
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Quick actions
    const quickActionBtns = document.querySelectorAll('.quick-action-btn');
    quickActionBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            // Add ripple effect
            createRippleEffect(this, e);
        });
    });
}

// ========== FILTER SYSTEM ==========
function initFilters() {
    const filterSelects = document.querySelectorAll('.filter-select');
    const searchInput = document.querySelector('.search-input');
    const quickFilterTags = document.querySelectorAll('.quick-filter-tag');
    
    // Filter change handlers
    filterSelects.forEach(select => {
        select.addEventListener('change', applyFilters);
    });
    
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                applyFilters();
            }, 300);
        });
        
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                applyFilters();
            }
        });
    }
    
    // Quick filter tags
    quickFilterTags.forEach(tag => {
        tag.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Update active state
            quickFilterTags.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Apply filter
            const filterValue = this.getAttribute('href').split('=')[1];
            const typeSelect = document.querySelector('select[name="type"]');
            if (typeSelect) {
                typeSelect.value = filterValue;
                applyFilters();
            }
        });
    });
}

function applyFilters() {
    const params = new URLSearchParams();
    
    // Collect filter values
    const typeFilter = document.querySelector('select[name="type"]')?.value;
    const techFilter = document.querySelector('select[name="tech"]')?.value;
    const sortFilter = document.querySelector('select[name="sort"]')?.value;
    const searchTerm = document.querySelector('.search-input')?.value;
    
    if (typeFilter) params.set('type', typeFilter);
    if (techFilter) params.set('tech', techFilter);
    if (sortFilter) params.set('sort', sortFilter);
    if (searchTerm) params.set('search', searchTerm);
    
    // Update URL and reload
    const newUrl = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
    window.location.href = newUrl;
}

// ========== DATA VISUALIZATIONS ==========
function initDataVisualizations() {
    // Initialize various chart types
    initRadarCharts();
    initDonutCharts();
    initBarCharts();
    initProgressCircles();
}

function initRadarCharts() {
    const radarCharts = document.querySelectorAll('.radar-chart');
    
    radarCharts.forEach(chart => {
        const values = chart.dataset.values?.split(',').map(v => parseFloat(v)) || [];
        const labels = chart.dataset.labels?.split(',') || [];
        const maxValue = parseFloat(chart.dataset.max) || 100;
        
        if (values.length && labels.length) {
            createRadarChart(chart, values, labels, maxValue);
        }
    });
}

function createRadarChart(container, values, labels, maxValue) {
    container.innerHTML = '';
    
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 200 200');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', '100%');
    
    const centerX = 100;
    const centerY = 100;
    const radius = 80;
    
    // Create radar rings
    for (let i = 1; i <= 5; i++) {
        const ring = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        ring.setAttribute('cx', centerX);
        ring.setAttribute('cy', centerY);
        ring.setAttribute('r', radius * (i / 5));
        ring.setAttribute('fill', 'none');
        ring.setAttribute('stroke', 'rgba(0, 240, 255, 0.1)');
        ring.setAttribute('stroke-width', '1');
        svg.appendChild(ring);
    }
    
    // Create axes and labels
    const numPoints = values.length;
    const angleStep = (2 * Math.PI) / numPoints;
    
    for (let i = 0; i < numPoints; i++) {
        const angle = i * angleStep - Math.PI / 2;
        const axisX = centerX + radius * Math.cos(angle);
        const axisY = centerY + radius * Math.sin(angle);
        
        // Axis line
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', centerX);
        line.setAttribute('y1', centerY);
        line.setAttribute('x2', axisX);
        line.setAttribute('y2', axisY);
        line.setAttribute('stroke', 'rgba(0, 240, 255, 0.2)');
        line.setAttribute('stroke-width', '1');
        svg.appendChild(line);
        
        // Label
        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        const labelX = centerX + (radius + 15) * Math.cos(angle);
        const labelY = centerY + (radius + 15) * Math.sin(angle);
        label.setAttribute('x', labelX);
        label.setAttribute('y', labelY);
        label.setAttribute('text-anchor', 'middle');
        label.setAttribute('dominant-baseline', 'middle');
        label.setAttribute('fill', 'rgba(255, 255, 255, 0.7)');
        label.setAttribute('font-size', '10');
        label.textContent = labels[i];
        svg.appendChild(label);
    }
    
    // Create data polygon
    const polygonPoints = [];
    for (let i = 0; i < numPoints; i++) {
        const angle = i * angleStep - Math.PI / 2;
        const value = values[i];
        const ratio = value / maxValue;
        const pointRadius = radius * ratio;
        
        const pointX = centerX + pointRadius * Math.cos(angle);
        const pointY = centerY + pointRadius * Math.sin(angle);
        
        polygonPoints.push(`${pointX},${pointY}`);
        
        // Data point
        const point = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        point.setAttribute('cx', pointX);
        point.setAttribute('cy', pointY);
        point.setAttribute('r', '3');
        point.setAttribute('fill', 'rgba(0, 240, 255, 0.8)');
        svg.appendChild(point);
    }
    
    // Data area
    const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    polygon.setAttribute('points', polygonPoints.join(' '));
    polygon.setAttribute('fill', 'rgba(0, 240, 255, 0.2)');
    polygon.setAttribute('stroke', 'rgba(0, 240, 255, 0.8)');
    polygon.setAttribute('stroke-width', '2');
    
    svg.insertBefore(polygon, svg.firstChild);
    container.appendChild(svg);
    
    // Animate the polygon
    setTimeout(() => {
        polygon.style.opacity = '0';
        polygon.style.transition = 'opacity 1s ease-in-out';
        polygon.getBoundingClientRect(); // Force reflow
        polygon.style.opacity = '1';
    }, 500);
}

function initDonutCharts() {
    const donutCharts = document.querySelectorAll('.usage-donut-chart');
    
    donutCharts.forEach(chart => {
        const segments = chart.querySelectorAll('.usage-segment');
        
        segments.forEach((segment, index) => {
            // Animate segments with delay
            setTimeout(() => {
                segment.style.strokeDashoffset = segment.getAttribute('data-offset') || '0';
            }, index * 200);
        });
    });
}

function initBarCharts() {
    const barCharts = document.querySelectorAll('.bar-chart');
    
    barCharts.forEach(chart => {
        const bars = chart.querySelectorAll('.bar');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    bars.forEach((bar, index) => {
                        const height = bar.dataset.height || bar.style.height;
                        bar.style.height = '0';
                        
                        setTimeout(() => {
                            bar.style.transition = 'height 1s ease-out';
                            bar.style.height = height;
                        }, index * 100);
                    });
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        observer.observe(chart);
    });
}

function initProgressCircles() {
    const progressCircles = document.querySelectorAll('.percentage-circle');
    
    progressCircles.forEach(circle => {
        const progressBar = circle.querySelector('.percentage-bar');
        if (progressBar) {
            const progress = progressBar.style.getPropertyValue('--progress') || '0';
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        setTimeout(() => {
                            progressBar.style.setProperty('--progress', progress);
                        }, 300);
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });
            
            observer.observe(circle);
        }
    });
}

// ========== TECHNOLOGY USAGE CHARTS ==========
function initTechUsageCharts() {
    const techItems = document.querySelectorAll('.tech-item');
    
    techItems.forEach((item, index) => {
        const usageFill = item.querySelector('.tech-usage-fill');
        if (usageFill) {
            const width = usageFill.style.width;
            usageFill.style.width = '0%';
            
            setTimeout(() => {
                usageFill.style.width = width;
            }, index * 100);
        }
    });
}

// ========== REAL-TIME UPDATES ==========
function initRealTimeUpdates() {
    const realTimeIndicator = document.querySelector('.real-time-indicator');
    
    if (realTimeIndicator) {
        // Simulate real-time data updates
        setInterval(() => {
            updateSystemMetrics();
            flashRealTimeIndicator();
        }, 30000); // Update every 30 seconds
    }
}

function updateSystemMetrics() {
    // Fetch updated metrics from API
    fetch('/api/systems/metrics/')
        .then(response => response.json())
        .then(data => {
            updateDashboardMetrics(data);
        })
        .catch(error => {
            console.log('Real-time update failed:', error);
        });
}

function updateDashboardMetrics(data) {
    // Update metric values with animation
    Object.keys(data).forEach(metricKey => {
        const metricElement = document.querySelector(`[data-metric="${metricKey}"]`);
        if (metricElement) {
            const currentValue = parseFloat(metricElement.textContent.replace(/[^\d.]/g, ''));
            const newValue = data[metricKey];
            const suffix = metricElement.textContent.replace(/[\d.]/g, '');
            
            animateNumber(metricElement, currentValue, newValue, 1000, suffix);
        }
    });
}

function flashRealTimeIndicator() {
    const indicator = document.querySelector('.real-time-indicator');
    if (indicator) {
        indicator.classList.add('active');
        setTimeout(() => {
            indicator.classList.remove('active');
        }, 2000);
    }
}

// ========== ANIMATIONS ==========
function initAnimations() {
    // Intersection Observer for scroll animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    // Observe elements for animation
    const animateElements = document.querySelectorAll('.system-card, .metric-card, .featured-system-card');
    animateElements.forEach(el => {
        observer.observe(el);
    });
    
    // Add CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        .system-card, .metric-card, .featured-system-card {
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.6s ease-out;
        }
        
        .animate-in {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
    `;
    document.head.appendChild(style);
}

// ========== UTILITY FUNCTIONS ==========
function animateNumber(element, start, end, duration, suffix = '') {
    const startTime = performance.now();
    const difference = end - start;
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function (ease-out)
        const easedProgress = 1 - Math.pow(1 - progress, 3);
        const currentValue = start + (difference * easedProgress);
        
        // Format number based on value
        let displayValue;
        if (currentValue >= 1000000) {
            displayValue = (currentValue / 1000000).toFixed(1) + 'M';
        } else if (currentValue >= 1000) {
            displayValue = (currentValue / 1000).toFixed(1) + 'K';
        } else if (currentValue % 1 !== 0) {
            displayValue = currentValue.toFixed(1);
        } else {
            displayValue = Math.round(currentValue);
        }
        
        element.textContent = displayValue + suffix;
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }
    
    requestAnimationFrame(updateNumber);
}

function createRippleEffect(element, event) {
    const ripple = document.createElement('span');
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
        background: rgba(0, 240, 255, 0.3);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s ease-out;
        pointer-events: none;
        z-index: 1;
    `;
    
    // Add ripple animation if not exists
    if (!document.getElementById('ripple-keyframes')) {
        const style = document.createElement('style');
        style.id = 'ripple-keyframes';
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(2);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function debounce(func, wait) {
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

// ========== SYSTEM DETAIL PAGE FUNCTIONALITY ==========
function initSystemDetail() {
    initGalleryLightbox();
    initMetricsGauges();
    initTechStackInteractions();
    initSystemNavigation();
}

function initGalleryLightbox() {
    const galleryImages = document.querySelectorAll('.gallery-image');
    
    galleryImages.forEach(img => {
        img.addEventListener('click', function() {
            openLightbox(this);
        });
    });
}

function openLightbox(img) {
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const lightboxCaption = document.getElementById('lightbox-caption');
    
    if (lightbox && lightboxImg) {
        lightbox.style.display = 'block';
        lightboxImg.src = img.src;
        lightboxCaption.textContent = img.alt;
        
        // Add fade-in animation
        setTimeout(() => {
            lightbox.style.opacity = '1';
        }, 10);
    }
}

function initMetricsGauges() {
    const gauges = document.querySelectorAll('.gauge-progress');
    
    gauges.forEach(gauge => {
        const progress = gauge.getAttribute('data-progress') || gauge.style.getPropertyValue('--progress');
        
        if (progress) {
            // Animate gauge
            setTimeout(() => {
                gauge.style.setProperty('--progress', progress);
            }, 500);
        }
    });
}

function initTechStackInteractions() {
    const techItems = document.querySelectorAll('.tech-item');
    
    techItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            // Highlight related technologies
            const techName = this.querySelector('.tech-name').textContent;
            highlightRelatedTech(techName);
        });
        
        item.addEventListener('mouseleave', function() {
            clearTechHighlights();
        });
    });
}

function highlightRelatedTech(techName) {
    // Add subtle highlighting logic for related technologies
    const allTechItems = document.querySelectorAll('.tech-item');
    allTechItems.forEach(item => {
        if (item.querySelector('.tech-name').textContent !== techName) {
            item.style.opacity = '0.5';
        }
    });
}

function clearTechHighlights() {
    const allTechItems = document.querySelectorAll('.tech-item');
    allTechItems.forEach(item => {
        item.style.opacity = '';
    });
}

function initSystemNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            // Add preview tooltip or hover effect
            this.style.transform = 'translateY(-2px)';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
}

// ========== ADMIN FUNCTIONALITY ==========
function initAdminInterface() {
    initFormEnhancements();
    initFileUploads();
    initFormValidation();
    initNotifications();
}

function initFormEnhancements() {
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        autoResize(textarea);
        textarea.addEventListener('input', () => autoResize(textarea));
    });
    
    // Enhanced select styling
    const selects = document.querySelectorAll('select');
    selects.forEach(select => {
        select.addEventListener('focus', function() {
            this.parentElement.classList.add('select-focused');
        });
        
        select.addEventListener('blur', function() {
            this.parentElement.classList.remove('select-focused');
        });
    });
}

function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

function initFileUploads() {
    const fileInputs = document.querySelectorAll('.file-upload-input');
    
    fileInputs.forEach(input => {
        const uploadArea = input.closest('.file-upload-area');
        
        if (uploadArea) {
            // Drag and drop
            uploadArea.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', function(e) {
                e.preventDefault();
                this.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    input.files = files;
                    handleFileUpload(input, files[0]);
                }
            });
            
            // File selection
            input.addEventListener('change', function() {
                if (this.files.length > 0) {
                    handleFileUpload(this, this.files[0]);
                }
            });
        }
    });
}

function handleFileUpload(input, file) {
    const uploadArea = input.closest('.file-upload-area');
    const uploadText = uploadArea.querySelector('.file-upload-text');
    
    if (uploadText) {
        uploadText.textContent = `Selected: ${file.name}`;
    }
    
    // Show progress bar (if implemented)
    showUploadProgress(uploadArea);
}

function showUploadProgress(uploadArea) {
    // Create progress bar
    const existingProgress = uploadArea.querySelector('.upload-progress');
    if (existingProgress) {
        existingProgress.remove();
    }
    
    const progressContainer = document.createElement('div');
    progressContainer.className = 'upload-progress';
    progressContainer.innerHTML = `
        <div class="upload-progress-bar" style="width: 0%"></div>
    `;
    
    uploadArea.appendChild(progressContainer);
    
    // Simulate upload progress
    const progressBar = progressContainer.querySelector('.upload-progress-bar');
    let progress = 0;
    
    const interval = setInterval(() => {
        progress += Math.random() * 20;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
        }
        progressBar.style.width = progress + '%';
    }, 200);
}

function initFormValidation() {
    const forms = document.querySelectorAll('.admin-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const isValid = validateForm(this);
            if (!isValid) {
                e.preventDefault();
            }
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', () => validateField(input));
            input.addEventListener('input', () => clearFieldError(input));
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    const fieldGroup = field.closest('.form-group');
    
    // Remove existing error states
    clearFieldError(field);
    
    // Check if required field is empty
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'This field is required');
        return false;
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showFieldError(field, 'Please enter a valid email address');
            return false;
        }
    }
    
    // URL validation
    if (field.type === 'url' && value) {
        try {
            new URL(value);
        } catch {
            showFieldError(field, 'Please enter a valid URL');
            return false;
        }
    }
    
    // Mark as valid
    fieldGroup.classList.add('success');
    return true;
}

function showFieldError(field, message) {
    const fieldGroup = field.closest('.form-group');
    fieldGroup.classList.add('error');
    
    // Remove existing error message
    const existingError = fieldGroup.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Add error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    field.parentNode.insertBefore(errorDiv, field.nextSibling);
}

function clearFieldError(field) {
    const fieldGroup = field.closest('.form-group');
    fieldGroup.classList.remove('error', 'success');
    
    const errorMessage = fieldGroup.querySelector('.error-message');
    if (errorMessage) {
        errorMessage.remove();
    }
}

function initNotifications() {
    // Auto-hide notifications
    const notifications = document.querySelectorAll('.admin-notification');
    
    notifications.forEach(notification => {
        // Show notification
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            hideNotification(notification);
        }, 5000);
        
        // Close button
        const closeBtn = notification.querySelector('.notification-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                hideNotification(notification);
            });
        }
    });
}

function hideNotification(notification) {
    notification.classList.remove('show');
    setTimeout(() => {
        notification.remove();
    }, 300);
}

function showNotification(type, title, message) {
    const notification = document.createElement('div');
    notification.className = `admin-notification ${type}`;
    notification.innerHTML = `
        <div class="notification-header">
            <div class="notification-title">${title}</div>
            <button class="notification-close">&times;</button>
        </div>
        <div class="notification-message">${message}</div>
    `;
    
    document.body.appendChild(notification);
    
    // Show with animation
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Set up close functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        hideNotification(notification);
    });
    
    // Auto-hide
    setTimeout(() => {
        hideNotification(notification);
    }, 5000);
}

// ========== EXPORT FUNCTIONS ==========
window.ProjectsJS = {
    initSystemDetail,
    initAdminInterface,
    showNotification,
    openLightbox,
    animateNumber,
    createRippleEffect
};

// Initialize based on page type
if (document.querySelector('.system-detail-page')) {
    initSystemDetail();
}

if (document.querySelector('.admin-page')) {
    initAdminInterface();
}