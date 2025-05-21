/**
 * ML DEVLOG - Base JavaScript
 * Interactive functionality for futuristic HUD-themed design system
 * Version: 1.1.0
 */

// Execute when DOM is fully loaded
document.addEventListener("DOMContentLoaded", function() {
    // ===== NAVBAR FUNCTIONALITY =====
    initNavbar();
    
    // ===== ANIMATION INITIALIZATION =====
    initAnimations();
    
    // ===== DATA VISUALIZATION DEMOS =====
    initDataVisualizations();
    
    // ===== CODE BLOCKS =====
    initCodeBlocks();
    
    // ===== HEX CATEGORIES =====
    initHexCategories();
    
    // ===== FORM VALIDATION =====
    initFormValidation();
});

// ===== NAVBAR FUNCTIONALITY =====
function initNavbar() {
    const navbar = document.querySelector('.navbar');
    const mobileToggle = document.querySelector('.navbar-mobile-toggle');
    const navbarMenu = document.querySelector('.navbar-menu');
    
    // Handle navbar background on scroll
    if (navbar) {
      window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
          navbar.classList.add('navbar-scrolled');
        } else {
          navbar.classList.remove('navbar-scrolled');
        }
      });
    }
    
// Mobile menu toggle
if (mobileToggle && navbarMenu) {
    mobileToggle.addEventListener('click', function() {
      navbarMenu.classList.toggle('active');
      // Toggle icon if using font awesome or similar
      if (this.querySelector('i')) {
        this.querySelector('i').classList.toggle('fa-bars');
        this.querySelector('i').classList.toggle('fa-times');
      }
    });
    
    // Observe all elements with animation class
    animatedElements.forEach(element => {
      observer.observe(element);
    });
  }
  
  // Init typing animations for elements with .typing-animation class
  const typingElements = document.querySelectorAll('.typing-animation');
  
  typingElements.forEach(element => {
    // Store original text to be animated
    const originalText = element.textContent;
    // Clear text initially
    element.textContent = '';
    
    // Set a short delay before starting animation
    setTimeout(() => {
      element.textContent = originalText;
    }, 500);
  });

  // Initialize scanning effects
  const scanningElements = document.querySelectorAll('.scanning-effect');
  // No additional initialization needed as scanning effect is CSS-only
  
  // Initialize glitch text effect
  const glitchElements = document.querySelectorAll('.glitch-text');
  // No additional initialization needed as glitch effect is CSS-only
  
  // Initialize pulse effect
  const pulseElements = document.querySelectorAll('.pulse-effect');
  // No additional initialization needed as pulse effect is CSS-only
}
  
// ===== DATA VISUALIZATION DEMOS =====
function initDataVisualizations() {
    // Circle Gauge Initialization
    initCircleGauges();
    
    // Initialize Bar Charts
    initBarCharts();
    
    // Initialize Waveform Visualizations
    initWaveforms();
    
    // Initialize Data Grids
    initDataGrids();
  }
  
// Initialize Circle Gauges
function initCircleGauges() {
    const gauges = document.querySelectorAll('.circle-gauge');
    
    gauges.forEach(gauge => {
      const percentValue = gauge.dataset.percent || 0;
      const valueElement = gauge.querySelector('.value');
      const progressCircle = gauge.querySelector('.progress');
      
      if (valueElement && progressCircle) {
        // Update the value display
        valueElement.textContent = `${percentValue}%`;
        
        // Calculate the stroke-dashoffset based on percentage
        // Formula: circumference - (circumference * percentValue / 100)
        const radius = progressCircle.getAttribute('r');
        const circumference = 2 * Math.PI * radius;
        const dashOffset = circumference - (circumference * percentValue / 100);
        
        // Apply the dash offset to show progress
        progressCircle.style.strokeDashoffset = dashOffset;
      }
    });
  }
  
// Initialize Bar Charts
function initBarCharts() {
    const barCharts = document.querySelectorAll('.bar-chart');
    
    barCharts.forEach(chart => {
      const bars = chart.querySelectorAll('.bar');
      
      bars.forEach(bar => {
        const value = bar.dataset.value || 0;
        const maxValue = bar.dataset.maxValue || 100;
        
        // Calculate height percentage
        const heightPercent = (value / maxValue) * 100;
        
        // Apply height with a slight delay for animation effect
        setTimeout(() => {
          bar.style.height = `${heightPercent}%`;
        }, 100);
      });
    });
  }
  
// Initialize Waveform Visualizations
function initWaveforms() {
    const waveforms = document.querySelectorAll('.waveform');
    
    waveforms.forEach(waveform => {
      // Generate bars based on data or create random visualization
      const dataValues = waveform.dataset.values;
      
      if (dataValues) {
        // Use provided data values
        const values = dataValues.split(',').map(val => parseFloat(val));
        createWaveformBars(waveform, values);
      } else {
        // Generate random waveform for demo
        const randomValues = Array.from({length: 50}, () => Math.random() * 100);
        createWaveformBars(waveform, randomValues);
        
        // Animate random waveform
        if (waveform.dataset.animate === 'true') {
          animateWaveform(waveform);
        }
      }
    });
  }
  
// Create bars for waveform visualization
function createWaveformBars(waveform, values) {
    waveform.innerHTML = ''; // Clear existing content
    
    values.forEach(value => {
      const bar = document.createElement('div');
      bar.className = 'waveform-bar';
      
      // Set height based on value (percentage of container height)
      bar.style.height = `${value}%`;
      
      waveform.appendChild(bar);
    });
  }
  
// Animate waveform with continuous random changes
function animateWaveform(waveform) {
    const bars = waveform.querySelectorAll('.waveform-bar');
    
    setInterval(() => {
      bars.forEach(bar => {
        // Generate new random height
        const newHeight = Math.random() * 100;
        bar.style.height = `${newHeight}%`;
      });
    }, 100); // Update every 100ms for a fluid animation
  }
  
// Initialize Data Grids
function initDataGrids() {
    const dataGrids = document.querySelectorAll('.data-grid');
    
    dataGrids.forEach(grid => {
      const cells = grid.querySelectorAll('.data-cell');
      
      // Check if grid should be randomized
      if (grid.dataset.random === 'true') {
        // Randomize active cells
        cells.forEach(cell => {
          if (Math.random() > 0.7) { // 30% chance of being active
            cell.classList.add('active');
          }
        });
        
        // If animation requested, periodically change active cells
        if (grid.dataset.animate === 'true') {
          setInterval(() => {
            cells.forEach(cell => {
              if (Math.random() > 0.7) {
                cell.classList.toggle('active');
              }
            });
          }, 800); // Change every 800ms
        }
      }
    });
  }
  
// ===== CODE BLOCKS =====
function initCodeBlocks() {
    const codeBlocks = document.querySelectorAll('.code-block');
    
    codeBlocks.forEach(block => {
      const codeHeader = block.querySelector('.code-header');
      
      // Add copy button if code header exists
      if (codeHeader) {
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.innerHTML = '<i class="fas fa-copy"></i>';
        copyButton.setAttribute('title', 'Copy code');
        
        // Append button to header
        codeHeader.appendChild(copyButton);
        
        // Add click handler
        copyButton.addEventListener('click', () => {
          const codeContent = block.querySelector('.code-content');
          
          if (codeContent) {
            // Get text content from pre or code element
            const codeToCopy = codeContent.querySelector('pre')?.textContent || 
                              codeContent.querySelector('code')?.textContent || 
                              codeContent.textContent;
            
            // Copy to clipboard
            navigator.clipboard.writeText(codeToCopy)
              .then(() => {
                // Show success state
                copyButton.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => {
                  copyButton.innerHTML = '<i class="fas fa-copy"></i>';
                }, 2000);
              })
              .catch(() => {
                // Show error state
                copyButton.innerHTML = '<i class="fas fa-times"></i>';
                setTimeout(() => {
                  copyButton.innerHTML = '<i class="fas fa-copy"></i>';
                }, 2000);
              });
          }
        });
      }
    });
    
    // Syntax highlighting if Prism.js or Highlight.js is included
    if (typeof Prism !== 'undefined') {
      Prism.highlightAll();
    } else if (typeof hljs !== 'undefined') {
      document.querySelectorAll('pre code').forEach(block => {
        hljs.highlightBlock(block);
      });
    }
  }
  
// ===== HEX CATEGORIES =====
function initHexCategories() {
    const categoryHexes = document.querySelectorAll('.category-hex');
    
    categoryHexes.forEach(hex => {
      // Add hover effect for category hexes
      hex.addEventListener('mouseover', function() {
        this.style.transform = 'scale(1.05)';
        
        // Get category color from CSS variable or data attribute
        const categoryColor = getComputedStyle(this).getPropertyValue('--category-color') || 
                             this.dataset.color || 
                             '#00f0ff';
        
        this.style.filter = `drop-shadow(0 0 8px ${categoryColor})`;
      });
      
      hex.addEventListener('mouseout', function() {
        this.style.transform = '';
        this.style.filter = '';
      });
    });
  }
  
// ===== FORM VALIDATION =====
function initFormValidation() {
    const forms = document.querySelectorAll('form.needs-validation');
    
    forms.forEach(form => {
      form.addEventListener('submit', function(event) {
        if (!this.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }
        
        this.classList.add('was-validated');
        
        // Add futuristic validation styling
        const invalidFields = this.querySelectorAll(':invalid');
        invalidFields.forEach(field => {
          field.parentElement.classList.add('field-error');
          
          // Add error message if not already present
          if (!field.nextElementSibling || !field.nextElementSibling.classList.contains('error-message')) {
            const errorMessage = document.createElement('div');
            errorMessage.className = 'error-message';
            errorMessage.textContent = field.validationMessage || 'This field is invalid';
            
            field.parentNode.insertBefore(errorMessage, field.nextSibling);
          }
        });
      }, false);
      
      // Clear validation styling on input
      const formInputs = form.querySelectorAll('input, textarea, select');
      formInputs.forEach(input => {
        input.addEventListener('input', function() {
          // Remove error styling when input changes
          this.parentElement.classList.remove('field-error');
          
          // Remove error message if it exists
          const errorMessage = this.nextElementSibling;
          if (errorMessage && errorMessage.classList.contains('error-message')) {
            errorMessage.remove();
          }
        });
      });
    });
  }
  
// ===== UTILITY FUNCTIONS =====

// Debounce function to limit how often a function is called
function debounce(func, wait) {
    let timeout;
    return function() {
      const context = this;
      const args = arguments;
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        func.apply(context, args);
      }, wait);
    };
  }
  
// Throttle function to limit the rate at which a function is executed
function throttle(func, limit) {
    let inThrottle;
    return function() {
      const context = this;
      const args = arguments;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }
  
// Generate a random number between min and max
function randomBetween(min, max) {
    return Math.floor(Math.random() * (max - min + 1) + min);
  }
  
// Check if an element is in viewport
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
  }
  
// Format number with comma separators
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }
  
// ===== OPTIONAL: HUD DATA ANIMATION DEMOS =====

// Initialize HUD-style data animation if elements exist
document.addEventListener("DOMContentLoaded", function() {
    if (document.querySelector('.hud-data-counter')) {
      initHUDDataCounters();
    }
    
    if (document.querySelector('.radar-chart')) {
      initRadarCharts();
    }
  });
  
// Animate number counters with HUD style
function initHUDDataCounters() {
    const counters = document.querySelectorAll('.hud-data-counter');
    
    counters.forEach(counter => {
      const target = parseInt(counter.dataset.target, 10);
      const duration = parseInt(counter.dataset.duration, 10) || 2000;
      const step = target / (duration / 16); // 60fps target
      let current = 0;
      
      const updateCounter = () => {
        current += step;
        if (current < target) {
          counter.textContent = Math.floor(current).toLocaleString();
          requestAnimationFrame(updateCounter);
        } else {
          counter.textContent = target.toLocaleString();
        }
      };
      
      // Start when element is in viewport
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            updateCounter();
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.5 });
      
      observer.observe(counter);
    });
  }
  
// Initialize radar charts
function initRadarCharts() {
    const radarCharts = document.querySelectorAll('.radar-chart');
    
    radarCharts.forEach(chart => {
      // Get data points from data attributes
      const dataPoints = chart.dataset.values.split(',').map(val => parseFloat(val));
      const labels = chart.dataset.labels?.split(',') || [];
      const maxValue = chart.dataset.max || 100;
      
      // Simple SVG-based radar chart
      if (dataPoints.length > 2) {
        createSVGRadarChart(chart, dataPoints, labels, maxValue);
      }
    });
  }
  
// Create SVG-based radar chart
function createSVGRadarChart(container, values, labels, maxValue) {
    // Clear container
    container.innerHTML = '';
    
    // Create SVG element
    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute("width", "100%");
    svg.setAttribute("height", "100%");
    svg.setAttribute("viewBox", "-10 -10 220 220");
    
    // Center point
    const centerX = 100;
    const centerY = 100;
    const radius = 90;
    
    // Add radar rings (background circles)
    for (let i = 1; i <= 5; i++) {
      const ring = document.createElementNS(svgNS, "circle");
      ring.setAttribute("cx", centerX);
      ring.setAttribute("cy", centerY);
      ring.setAttribute("r", radius * (i/5));
      ring.setAttribute("fill", "none");
      ring.setAttribute("stroke", "rgba(0, 240, 255, 0.2)");
      ring.setAttribute("stroke-width", "1");
      svg.appendChild(ring);
    }
    
    // Add axes
    const numPoints = values.length;
    const angleStep = (2 * Math.PI) / numPoints;
    
    for (let i = 0; i < numPoints; i++) {
      const angle = i * angleStep - Math.PI/2; // Start from top
      const axisX = centerX + radius * Math.cos(angle);
      const axisY = centerY + radius * Math.sin(angle);
      
      const axis = document.createElementNS(svgNS, "line");
      axis.setAttribute("x1", centerX);
      axis.setAttribute("y1", centerY);
      axis.setAttribute("x2", axisX);
      axis.setAttribute("y2", axisY);
      axis.setAttribute("stroke", "rgba(0, 240, 255, 0.2)");
      axis.setAttribute("stroke-width", "1");
      svg.appendChild(axis);
      
      // Add label if available
      if (labels[i]) {
        const label = document.createElementNS(svgNS, "text");
        // Position label slightly beyond the axis end
        const labelX = centerX + (radius + 15) * Math.cos(angle);
        const labelY = centerY + (radius + 15) * Math.sin(angle);
        
        label.setAttribute("x", labelX);
        label.setAttribute("y", labelY);
        label.setAttribute("text-anchor", "middle");
        label.setAttribute("alignment-baseline", "middle");
        label.setAttribute("fill", "#aaaaaa");
        label.setAttribute("font-size", "10");
        label.textContent = labels[i];
        svg.appendChild(label);
      }
    }
    
    // Create data polygon
    const polygonPoints = [];
    
    for (let i = 0; i < numPoints; i++) {
      const angle = i * angleStep - Math.PI/2; // Start from top
      const value = values[i];
      const valueRatio = value / maxValue;
      const pointRadius = radius * valueRatio;
      
      const pointX = centerX + pointRadius * Math.cos(angle);
      const pointY = centerY + pointRadius * Math.sin(angle);
      
      polygonPoints.push(`${pointX},${pointY}`);
      
      // Add point marker
      const point = document.createElementNS(svgNS, "circle");
      point.setAttribute("cx", pointX);
      point.setAttribute("cy", pointY);
      point.setAttribute("r", "4");
      point.setAttribute("fill", "rgba(0, 240, 255, 0.8)");
      svg.appendChild(point);
    }
    
    // Create data polygon
    const polygon = document.createElementNS(svgNS, "polygon");
    polygon.setAttribute("points", polygonPoints.join(" "));
    polygon.setAttribute("fill", "rgba(0, 240, 255, 0.2)");
    polygon.setAttribute("stroke", "rgba(0, 240, 255, 0.8)");
    polygon.setAttribute("stroke-width", "2");
    
    // Insert polygon before points for proper z-index
    if (svg.firstChild) {
      svg.insertBefore(polygon, svg.firstChild);
    } else {
      svg.appendChild(polygon);
    }
    
    container.appendChild(svg);
  }
  
// Close mobile menu when clicking outside
document.addEventListener('click', function(event) {
    if (navbarMenu.classList.contains('active') && 
        !navbarMenu.contains(event.target) && 
        !mobileToggle.contains(event.target)) {
      navbarMenu.classList.remove('active');
      
      // Reset icon if using font awesome
      if (mobileToggle.querySelector('i')) {
        mobileToggle.querySelector('i').classList.add('fa-bars');
        mobileToggle.querySelector('i').classList.remove('fa-times');
      }
    }
  });
}

    
    // Handle smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]:not([href="#"])');
    
    anchorLinks.forEach(link => {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        const targetElement = document.querySelector(targetId);
        
        if (targetElement) {
          // Close mobile menu if open
          if (navbarMenu && navbarMenu.classList.contains('active')) {
            navbarMenu.classList.remove('active');
            
            if (mobileToggle && mobileToggle.querySelector('i')) {
              mobileToggle.querySelector('i').classList.add('fa-bars');
              mobileToggle.querySelector('i').classList.remove('fa-times');
            }
          }
          
          // Calculate scroll position considering navbar height
          const navbarHeight = navbar ? navbar.offsetHeight : 0;
          const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset;
          
          window.scrollTo({
            top: targetPosition - navbarHeight - 20, // Extra 20px for padding
            behavior: 'smooth'
          });
        }
      });
    });
  
  
  // ===== ANIMATION INITIALIZATION =====
  function initAnimations() {
    // Init animation on scroll (for elements with .animate-on-scroll class)
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animatedElements.length > 0) {
      // Simple intersection observer for animations
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            // Get animation type from data attribute or default to fade-in
            const animationType = entry.target.dataset.animation || 'fade-in';
            entry.target.classList.add(animationType);
            
            // Unobserve after animation triggered
            observer.unobserve(entry.target);
          }
        });
          }, { threshold: 0.2 });
        }
      }