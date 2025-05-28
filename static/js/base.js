/**
 * AURA Portfolio - Base JavaScript
 * Advanced User Repository & Archive - Core System Functions
 * Version: 2.0.1 - Component Architecture
 */

// AURA System State
const AURA = {
  initialized: false,
  loadingComplete: false,
  components: {
      navigation: false,
      forms: false,
      dashboard: false,
      animations: false
  },
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
  initScrollAnimations();
  initComponentAnimations();
  
  // Initialize component systems
  initComponentSystems();
  
  // Initialize loading sequence if on homepage
  if (document.querySelector('#loadingScreen')) {
      initLoadingSequence();
  }
  
  // Mark as initialized
  AURA.initialized = true;
  console.log('✅ AURA System Online');
}

/**
* Form Component Enhancements
*/
function initFormComponents() {
  // Initialize form scanning effects
  initFormScanningEffects();
  
  // Initialize form validation enhancements
  initFormValidation();
  
  // Initialize file upload enhancements
  initFileUploadEnhancements();
  
  // Initialize form auto-save (if needed)
  initFormAutoSave();
}

/**
* Form scanning line effects
*/
function initFormScanningEffects() {
  const formControls = document.querySelectorAll('.form-control, .form-select');
  
  formControls.forEach(control => {
      const container = control.closest('.input-container');
      if (!container) return;
      
      control.addEventListener('focus', function() {
          container.classList.add('scanning');
      });
      
      control.addEventListener('blur', function() {
          container.classList.remove('scanning');
      });
  });
}

/**
* Enhanced form validation
*/
function initFormValidation() {
  const forms = document.querySelectorAll('.aura-form');
  
  forms.forEach(form => {
      const inputs = form.querySelectorAll('.form-control, .form-select');
      
      inputs.forEach(input => {
          input.addEventListener('blur', function() {
              validateField(this);
          });
          
          input.addEventListener('input', debounce(function() {
              if (this.classList.contains('is-invalid')) {
                  validateField(this);
              }
          }, 300));
      });
      
      form.addEventListener('submit', function(event) {
          let isValid = true;
          
          inputs.forEach(input => {
              if (!validateField(input)) {
                  isValid = false;
              }
          });
          
          if (!isValid) {
              event.preventDefault();
              
              // Focus first invalid field
              const firstInvalid = form.querySelector('.form-control.is-invalid, .form-select.is-invalid');
              if (firstInvalid) {
                  firstInvalid.focus();
              }
          }
      });
  });
}

/**
* Validate individual form field
*/
function validateField(field) {
  const value = field.value.trim();
  const isRequired = field.hasAttribute('required');
  const fieldType = field.type || field.tagName.toLowerCase();
  
  // Remove existing validation classes
  field.classList.remove('is-valid', 'is-invalid');
  
  // Remove existing feedback
  const existingFeedback = field.parentNode.querySelector('.form-feedback');
  if (existingFeedback) {
      existingFeedback.remove();
  }
  
  let isValid = true;
  let message = '';
  
  // Required field validation
  if (isRequired && !value) {
      isValid = false;
      message = 'This field is required.';
  }
  
  // Email validation
  else if (fieldType === 'email' && value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) {
          isValid = false;
          message = 'Please enter a valid email address.';
      }
  }
  
  // URL validation
  else if (fieldType === 'url' && value) {
      try {
          new URL(value);
      } catch {
          isValid = false;
          message = 'Please enter a valid URL.';
      }
  }
  
  // Apply validation styling
  field.classList.add(isValid ? 'is-valid' : 'is-invalid');
  
  // Add feedback message
  if (!isValid && message) {
      const feedback = document.createElement('div');
      feedback.className = 'form-feedback invalid';
      feedback.textContent = message;
      field.parentNode.appendChild(feedback);
  }
  
  return isValid;
}

/**
* File upload enhancements
*/
function initFileUploadEnhancements() {
  const fileInputs = document.querySelectorAll('.file-upload-input');
  
  fileInputs.forEach(input => {
      const label = input.parentNode.querySelector('.file-upload-label');
      if (!label) return;
      
      input.addEventListener('change', function() {
          const files = this.files;
          const fileText = label.querySelector('.file-upload-text');
          
          if (files.length > 0) {
              const fileNames = Array.from(files).map(file => file.name).join(', ');
              fileText.textContent = `Selected: ${fileNames}`;
              label.classList.add('has-files');
          } else {
              fileText.textContent = 'Choose file or drag and drop';
              label.classList.remove('has-files');
          }
      });
      
      // Drag and drop functionality
      ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
          label.addEventListener(eventName, preventDefaults, false);
      });
      
      ['dragenter', 'dragover'].forEach(eventName => {
          label.addEventListener(eventName, () => label.classList.add('drag-over'), false);
      });
      
      ['dragleave', 'drop'].forEach(eventName => {
          label.addEventListener(eventName, () => label.classList.remove('drag-over'), false);
      });
      
      label.addEventListener('drop', function(event) {
          const dt = event.dataTransfer;
          const files = dt.files;
          input.files = files;
          
          // Trigger change event
          const changeEvent = new Event('change', { bubbles: true });
          input.dispatchEvent(changeEvent);
      });
  });
}

/**
* Prevent default drag behaviors
*/
function preventDefaults(event) {
  event.preventDefault();
  event.stopPropagation();
}

/**
* Form auto-save functionality
*/
function initFormAutoSave() {
  const autoSaveForms = document.querySelectorAll('[data-auto-save]');
  
  autoSaveForms.forEach(form => {
      const formId = form.dataset.autoSave;
      const inputs = form.querySelectorAll('input, textarea, select');
      
      // Load saved data
      loadFormData(form, formId);
      
      // Save data on input
      inputs.forEach(input => {
          input.addEventListener('input', debounce(() => {
              saveFormData(form, formId);
          }, 1000));
      });
      
      // Clear saved data on successful submit
      form.addEventListener('submit', () => {
          clearFormData(formId);
      });
  });
}

/**
* Save form data to localStorage
*/
function saveFormData(form, formId) {
  const formData = new FormData(form);
  const data = {};
  
  for (let [key, value] of formData.entries()) {
      data[key] = value;
  }
  
  try {
      localStorage.setItem(`aura_form_${formId}`, JSON.stringify(data));
  } catch (error) {
      console.warn('Could not save form data:', error);
  }
}

/**
* Load form data from localStorage
*/
function loadFormData(form, formId) {
  try {
      const saved = localStorage.getItem(`aura_form_${formId}`);
      if (saved) {
          const data = JSON.parse(saved);
          
          Object.keys(data).forEach(key => {
              const input = form.querySelector(`[name="${key}"]`);
              if (input && input.type !== 'file') {
                  input.value = data[key];
              }
          });
      }
  } catch (error) {
      console.warn('Could not load form data:', error);
  }
}

/**
* Clear saved form data
*/
function clearFormData(formId) {
  try {
      localStorage.removeItem(`aura_form_${formId}`);
  } catch (error) {
      console.warn('Could not clear form data:', error);
  }
}

/**
* Dashboard Component Enhancements
*/
function initDashboardComponents() {
  // Initialize widget interactions
  initWidgetInteractions();
  
  // Initialize dashboard animations
  initDashboardAnimations();
  
  // Initialize real-time updates
  initRealTimeUpdates();
}

/**
* Widget interaction enhancements
*/
function initWidgetInteractions() {
  const widgets = document.querySelectorAll('.dashboard-widget');
  
  widgets.forEach(widget => {
      // Widget action buttons
      const actions = widget.querySelectorAll('.widget-action');
      actions.forEach(action => {
          action.addEventListener('click', function() {
              const actionType = this.dataset.action;
              handleWidgetAction(widget, actionType);
          });
      });
      
      // Widget hover effects
      widget.addEventListener('mouseenter', function() {
          this.classList.add('widget-focused');
      });
      
      widget.addEventListener('mouseleave', function() {
          this.classList.remove('widget-focused');
      });
  });
}

/**
* Handle widget actions
*/
function handleWidgetAction(widget, actionType) {
  switch (actionType) {
      case 'refresh':
          refreshWidget(widget);
          break;
      case 'minimize':
          minimizeWidget(widget);
          break;
      case 'maximize':
          maximizeWidget(widget);
          break;
      case 'settings':
          openWidgetSettings(widget);
          break;
  }
}

/**
* Refresh widget data
*/
function refreshWidget(widget) {
  widget.classList.add('widget-loading');
  
  // Simulate data refresh
  setTimeout(() => {
      widget.classList.remove('widget-loading');
      
      // Add refresh animation
      widget.style.transform = 'scale(1.02)';
      setTimeout(() => {
          widget.style.transform = '';
      }, 200);
  }, 1000);
}

/**
* Dashboard animations
*/
function initDashboardAnimations() {
  // Animate dashboard on load
  const dashboardContainer = document.querySelector('.dashboard-container');
  if (dashboardContainer) {
      const widgets = dashboardContainer.querySelectorAll('.dashboard-widget');
      
      widgets.forEach((widget, index) => {
          widget.style.opacity = '0';
          widget.style.transform = 'translateY(20px)';
          
          setTimeout(() => {
              widget.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
              widget.style.opacity = '1';
              widget.style.transform = 'translateY(0)';
          }, index * 100);
      });
  }
}

/**
* Real-time dashboard updates
*/
function initRealTimeUpdates() {
  // Update metrics every 30 seconds
  setInterval(() => {
      updateDashboardMetrics();
  }, 30000);
  
  // Update activity feed every 60 seconds
  setInterval(() => {
      updateActivityFeed();
  }, 60000);
}

/**
* Update dashboard metrics
*/
function updateDashboardMetrics() {
  const metricValues = document.querySelectorAll('[data-metric]');
  
  metricValues.forEach(element => {
      const metricType = element.dataset.metric;
      
      switch (metricType) {
          case 'uptime':
              // Simulate slight uptime changes
              const currentUptime = parseFloat(element.textContent);
              const newUptime = Math.max(99.5, Math.min(99.9, currentUptime + (Math.random() - 0.5) * 0.1));
              element.textContent = newUptime.toFixed(1) + '%';
              break;
              
          case 'response_time':
              // Simulate response time changes
              const newResponseTime = Math.floor(Math.random() * 60) + 120;
              element.textContent = newResponseTime + 'ms';
              break;
      }
  });
}

/**
* Update activity feed
*/
function updateActivityFeed() {
  const activityFeeds = document.querySelectorAll('.activity-list');
  
  activityFeeds.forEach(feed => {
      // Add subtle animation to indicate update
      feed.style.opacity = '0.7';
      setTimeout(() => {
          feed.style.opacity = '1';
      }, 300);
  });
}

/**
* Animation Component Enhancements
*/
function initAnimationComponents() {
  // Initialize entrance animations
  initEntranceAnimations();
  
  // Initialize hover animations
  initHoverAnimations();
  
  // Initialize loading animations
  initLoadingAnimations();
}

/**
* Entrance animations for elements
*/
function initEntranceAnimations() {
  const animatedElements = document.querySelectorAll('[data-animate]');
  
  const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
          if (entry.isIntersecting) {
              const element = entry.target;
              const animationType = element.dataset.animate;
              
              element.classList.add(`animate-${animationType}`);
              observer.unobserve(element);
          }
      });
  }, { threshold: 0.1 });
  
  animatedElements.forEach(element => {
      observer.observe(element);
  });
}

/**
* Hover animations
*/
function initHoverAnimations() {
  const hoverElements = document.querySelectorAll('.hover-glow, .hover-lift');
  
  hoverElements.forEach(element => {
      element.addEventListener('mouseenter', function() {
          this.classList.add('hovered');
      });
      
      element.addEventListener('mouseleave', function() {
          this.classList.remove('hovered');
      });
  });
}

/**
* Loading animations
*/
function initLoadingAnimations() {
  const loadingElements = document.querySelectorAll('.shimmer-effect');
  
  // Add intersection observer to start shimmer when visible
  const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
          if (entry.isIntersecting) {
              entry.target.classList.add('shimmer-active');
          } else {
              entry.target.classList.remove('shimmer-active');
          }
      });
  });
  
  loadingElements.forEach(element => {
      observer.observe(element);
  });
}