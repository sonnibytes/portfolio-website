/**
 * core/static/core/js/home.js
 * JavaScript for the homepage with interactive elements
 */

document.addEventListener('DOMContentLoaded', function() {
    // ===== TERMINAL TYPING EFFECT =====
    initTerminalEffect();
    
    // ===== RADAR CHART VISUALIZATION =====
    initRadarChart();
    
    // ===== DATA GRID ANIMATION =====
    initDataGrid();
    
    // ===== ANIMATE SKILL BARS ON SCROLL =====
    initSkillBars();
    
    // ===== SCROLL ANIMATIONS =====
    initScrollAnimations();
  });
  
  // Terminal typing effect
  function initTerminalEffect() {
    const terminalLines = document.querySelectorAll('.terminal-line');
    const terminalOutputs = document.querySelectorAll('.terminal-output');
    
    // Hide all lines and outputs initially
    terminalLines.forEach(line => line.style.opacity = '0');
    terminalOutputs.forEach(output => output.style.opacity = '0');
    
    // Function to animate each line and its corresponding output
    function animateTerminal(lineIndex = 0) {
      if (lineIndex >= terminalLines.length) return;
      
      const line = terminalLines[lineIndex];
      const output = terminalOutputs[lineIndex];
      
      // Show and animate typing for the line
      line.style.opacity = '1';
      typeText(line, line.textContent, 0, 50, () => {
        // After line is typed, show the output
        if (output) {
          setTimeout(() => {
            output.style.opacity = '1';
            
            // Move to next line after output is shown
            setTimeout(() => {
              animateTerminal(lineIndex + 1);
            }, 500);
          }, 300);
        } else {
          // If no output, move to next line
          animateTerminal(lineIndex + 1);
        }
      });
    }
    
    // Start the animation
    setTimeout(() => {
      animateTerminal();
    }, 500);
  }
  
  // Function to simulate typing text
  function typeText(element, text, index, speed, callback) {
    if (index < text.length) {
      element.textContent = text.substring(0, index + 1);
      setTimeout(() => {
        typeText(element, text, index + 1, speed, callback);
      }, speed);
    } else if (callback) {
      callback();
    }
  }
  
  // Initialize Radar Chart
  function initRadarChart() {
    const radarChart = document.querySelector('.radar-chart');
    
    if (!radarChart) return;
    
    // Get data from data attributes
    const values = radarChart.dataset.values.split(',').map(val => parseFloat(val));
    const labels = radarChart.dataset.labels.split(',');
    const maxValue = parseFloat(radarChart.dataset.max || '100');
    
    // Create SVG element
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', '100%');
    svg.setAttribute('viewBox', '0 0 200 200');
    
    // Create radar web (rings)
    for (let r = 1; r <= 5; r++) {
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('cx', '100');
      circle.setAttribute('cy', '100');
      circle.setAttribute('r', r * 20);
      circle.setAttribute('fill', 'none');
      circle.setAttribute('stroke', 'rgba(0, 240, 255, 0.1)');
      circle.setAttribute('stroke-width', '1');
      svg.appendChild(circle);
    }
    
    // Create axes
    const numAxes = labels.length;
    for (let i = 0; i < numAxes; i++) {
      const angle = (Math.PI * 2 * i) / numAxes - Math.PI / 2;
      const x = 100 + 100 * Math.cos(angle);
      const y = 100 + 100 * Math.sin(angle);
      
      // Draw axis line
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', '100');
      line.setAttribute('y1', '100');
      line.setAttribute('x2', x);
      line.setAttribute('y2', y);
      line.setAttribute('stroke', 'rgba(0, 240, 255, 0.2)');
      line.setAttribute('stroke-width', '1');
      svg.appendChild(line);
      
      // Add label
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      const labelX = 100 + 110 * Math.cos(angle);
      const labelY = 100 + 110 * Math.sin(angle);
      text.setAttribute('x', labelX);
      text.setAttribute('y', labelY);
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('dominant-baseline', 'middle');
      text.setAttribute('fill', 'rgba(255, 255, 255, 0.7)');
      text.setAttribute('font-size', '10');
      text.textContent = labels[i];
      svg.appendChild(text);
    }
    
    // Create data polygon
    const polygonPoints = [];
    for (let i = 0; i < numAxes; i++) {
      const angle = (Math.PI * 2 * i) / numAxes - Math.PI / 2;
      const value = values[i];
      const ratio = value / maxValue;
      const radian = ratio * 100; // Scale to fit within 100px radius
      
      const x = 100 + radian * Math.cos(angle);
      const y = 100 + radian * Math.sin(angle);
      polygonPoints.push(`${x},${y}`);
      
      // Add point
      const point = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      point.setAttribute('cx', x);
      point.setAttribute('cy', y);
      point.setAttribute('r', '3');
      point.setAttribute('fill', 'rgba(0, 240, 255, 1)');
      svg.appendChild(point);
    }
    
    // Create filled polygon
    const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    polygon.setAttribute('points', polygonPoints.join(' '));
    polygon.setAttribute('fill', 'rgba(0, 240, 255, 0.2)');
    polygon.setAttribute('stroke', 'rgba(0, 240, 255, 0.7)');
    polygon.setAttribute('stroke-width', '2');
    
    // Insert polygon before points for proper layering
    svg.insertBefore(polygon, svg.firstChild);
    
    // Add SVG to container
    radarChart.appendChild(svg);
    
    // Add animation to show the chart
    setTimeout(() => {
      polygon.style.opacity = '0';
      polygon.style.transition = 'opacity 1s ease-in-out';
      polygon.getBoundingClientRect(); // Force reflow
      polygon.style.opacity = '1';
    }, 500);
  }
  
  // Initialize Data Grid Animation
  function initDataGrid() {
    const dataGrid = document.querySelector('.data-grid');
    
    if (!dataGrid) return;
    
    // Create grid cells
    const columns = 20;
    const rows = 20;
    
    for (let i = 0; i < rows; i++) {
      for (let j = 0; j < columns; j++) {
        const cell = document.createElement('div');
        cell.className = 'data-cell';
        dataGrid.appendChild(cell);
      }
    }
    
    // Set grid template
    dataGrid.style.gridTemplateColumns = `repeat(${columns}, 1fr)`;
    dataGrid.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
    
    // Animate cells
    const cells = dataGrid.querySelectorAll('.data-cell');
    
    function animateCells() {
      cells.forEach((cell) => {
        if (Math.random() > 0.7) {
          cell.classList.toggle('active');
        }
      });
    }
    
    // Run animation every 800ms
    setInterval(animateCells, 800);
  }
  
  // Initialize Skill Bars Animation
  function initSkillBars() {
    const skillBars = document.querySelectorAll('.skill-progress');
    
    if (skillBars.length === 0) return;
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const progressBar = entry.target.querySelector('.skill-progress-bar');
          if (progressBar) {
            progressBar.style.width = progressBar.dataset.width || '0%';
          }
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.2 });
    
    skillBars.forEach(skillBar => {
      const progressBar = skillBar.querySelector('.skill-progress-bar');
      if (progressBar) {
        // Store the width temporarily
        progressBar.dataset.width = progressBar.style.width;
        progressBar.style.width = '0';
        
        observer.observe(skillBar);
      }
    });
  }
  
  // Initialize Scroll Animations
  function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.fade-in, .slide-in-up');
    
    if (animatedElements.length === 0) return;
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animated');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    
    animatedElements.forEach(element => {
      observer.observe(element);
    });
  }
  
  /**
   * core/static/core/js/about.js
   * JavaScript for the about page
   */
  
  document.addEventListener('DOMContentLoaded', function() {
    // ===== SKILL BARS ANIMATION =====
    initSkillBars();
    
    // ===== TIMELINE ANIMATION =====
    initTimelineAnimation();
  });
  
  // Initialize Skill Bars Animation
  function initSkillBars() {
    const skillBars = document.querySelectorAll('.progress-indicator');
    
    if (skillBars.length === 0) return;
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const progressBar = entry.target.querySelector('.progress-bar');
          if (progressBar) {
            progressBar.style.width = progressBar.dataset.width || '0%';
          }
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.2 });
    
    skillBars.forEach(skillBar => {
      const progressBar = skillBar.querySelector('.progress-bar');
      if (progressBar) {
        // Get width from style (set in the template)
        const width = progressBar.style.width;
        // Store the width temporarily
        progressBar.dataset.width = width;
        progressBar.style.width = '0';
        
        observer.observe(skillBar);
      }
    });
  }
  
  // Initialize Timeline Animation
  function initTimelineAnimation() {
    const timelineItems = document.querySelectorAll('.timeline-item');
    
    if (timelineItems.length === 0) return;
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.2 });
    
    // Add CSS for animation
    const style = document.createElement('style');
    style.textContent = `
      .timeline-item {
        opacity: 0;
        transform: translateX(-30px);
        transition: all 0.8s ease-out;
      }
      
      .timeline-item.right {
        transform: translateX(30px);
      }
      
      .timeline-item.revealed {
        opacity: 1;
        transform: translateX(0);
      }
    `;
    document.head.appendChild(style);
    
    timelineItems.forEach(item => {
      observer.observe(item);
    });
  }
  
  /**
   * core/static/core/js/contact.js
   * JavaScript for the contact page
   */
  
  document.addEventListener('DOMContentLoaded', function() {
    // ===== FORM VALIDATION =====
    initFormValidation();
    
    // ===== SOCIAL ICONS ANIMATION =====
    initSocialIconsAnimation();
  });
  
  // Initialize Form Validation
  function initFormValidation() {
      const contactForm = document.querySelector('.contact-form');
      
      if (!contactForm) return;
  
      // Add validation class to form
      contactForm.classList.add('needs-validation');
      
      // Add styles for validation
      const style = document.createElement('style');
      style.textContent = `
        .form-group.error .form-control {
          border-color: var(--color-coral);
          box-shadow: 0 0 0 0.2rem rgba(255, 107, 139, 0.25);
        }
        
        .error-message {
          color: var(--color-coral);
          font-size: 0.85rem;
          margin-top: 0.5rem;
          display: none;
        }
        
        .form-group.error .error-message {
          display: block;
        }
        
        .form-control.valid {
          border-color: #27c93f;
          box-shadow: 0 0 0 0.2rem rgba(39, 201, 63, 0.25);
        }
      `;
      document.head.appendChild(style);
      
      // Handle form submission
      contactForm.addEventListener('submit', function(e) {
        let isValid = true;
        
        // Remove all error classes first
        const formGroups = contactForm.querySelectorAll('.form-group');
        formGroups.forEach(group => {
          group.classList.remove('error');
          const control = group.querySelector('.form-control');
          if (control) control.classList.remove('valid');
        });
        
        // Check each required field
        const requiredFields = contactForm.querySelectorAll('[required]');
        requiredFields.forEach(field => {
          if (!field.value.trim()) {
            isValid = false;
            field.parentElement.classList.add('error');
            
            // Add error message if not exists
            let errorMsg = field.parentElement.querySelector('.error-message');
            if (!errorMsg) {
              errorMsg = document.createElement('div');
              errorMsg.className = 'error-message';
              errorMsg.textContent = 'This field is required';
              field.parentElement.appendChild(errorMsg);
            }
          } else {
            field.classList.add('valid');
          }
        });
        
        // Check email format
        const emailField = contactForm.querySelector('input[type="email"]');
        if (emailField && emailField.value.trim()) {
          const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          if (!emailPattern.test(emailField.value)) {
            isValid = false;
            emailField.parentElement.classList.add('error');
            
            // Add error message if not exists
            let errorMsg = emailField.parentElement.querySelector('.error-message');
            if (!errorMsg) {
              errorMsg = document.createElement('div');
              errorMsg.className = 'error-message';
              errorMsg.textContent = 'Please enter a valid email address';
              emailField.parentElement.appendChild(errorMsg);
            } else {
              errorMsg.textContent = 'Please enter a valid email address';
            }
          }
        }
        
        // If form is not valid, prevent submission
        if (!isValid) {
          e.preventDefault();
          e.stopPropagation();
          
          // Scroll to first error
          const firstError = contactForm.querySelector('.form-group.error');
          if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        } else {
          // Add loading state to submit button
          const submitBtn = contactForm.querySelector('button[type="submit"]');
          if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin me-2"></i> Sending...';
          }
        }
      });
      
      // Add live validation on input
      const formInputs = contactForm.querySelectorAll('.form-control');
      formInputs.forEach(input => {
        input.addEventListener('input', function() {
          // Remove error state when typing
          this.parentElement.classList.remove('error');
          this.classList.remove('valid');
          
          // Remove error message
          const errorMsg = this.parentElement.querySelector('.error-message');
          if (errorMsg) errorMsg.style.display = 'none';
        });
        
        input.addEventListener('blur', function() {
          // Validate on blur
          if (this.hasAttribute('required') && !this.value.trim()) {
            this.parentElement.classList.add('error');
            let errorMsg = this.parentElement.querySelector('.error-message');
            if (!errorMsg) {
              errorMsg = document.createElement('div');
              errorMsg.className = 'error-message';
              errorMsg.textContent = 'This field is required';
              this.parentElement.appendChild(errorMsg);
            } else {
              errorMsg.style.display = 'block';
            }
          } else if (this.type === 'email' && this.value.trim()) {
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(this.value)) {
              this.parentElement.classList.add('error');
              let errorMsg = this.parentElement.querySelector('.error-message');
              if (!errorMsg) {
                errorMsg = document.createElement('div');
                errorMsg.className = 'error-message';
                errorMsg.textContent = 'Please enter a valid email address';
                this.parentElement.appendChild(errorMsg);
              } else {
                errorMsg.textContent = 'Please enter a valid email address';
                errorMsg.style.display = 'block';
              }
            } else {
              this.classList.add('valid');
            }
          } else if (this.value.trim()) {
            this.classList.add('valid');
          }
        });
      });
    }
    
    // Initialize Social Icons Animation
    function initSocialIconsAnimation() {
      const socialIcons = document.querySelectorAll('.social-icon');
      
      if (socialIcons.length === 0) return;
      
      socialIcons.forEach((icon, index) => {
        // Add delay to stagger animations
        icon.style.opacity = '0';
        icon.style.transform = 'translateY(20px)';
        icon.style.transition = 'all 0.5s ease-out';
        
        setTimeout(() => {
          icon.style.opacity = '1';
          icon.style.transform = 'translateY(0)';
        }, 100 * index);
      });
    }
    
    /**
     * core/static/core/js/resume.js
     * JavaScript for the resume page
     */
    
    document.addEventListener('DOMContentLoaded', function() {
      // ===== SKILL TAGS ANIMATION =====
      initSkillTagsAnimation();
      
      // ===== EXPERIENCE ITEMS ANIMATION =====
      initExperienceAnimation();
      
      // ===== EDUCATION ITEMS ANIMATION =====
      initEducationAnimation();
    });
    
    // Initialize Skill Tags Animation
    function initSkillTagsAnimation() {
      const skillGroups = document.querySelectorAll('.skill-group');
      
      if (skillGroups.length === 0) return;
      
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const skillTags = entry.target.querySelectorAll('.skill-tag');
            
            skillTags.forEach((tag, index) => {
              setTimeout(() => {
                tag.style.opacity = '1';
                tag.style.transform = 'translateY(0)';
              }, 50 * index);
            });
            
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.2 });
      
      // Add CSS for animation
      const style = document.createElement('style');
      style.textContent = `
        .skill-tag {
          opacity: 0;
          transform: translateY(10px);
          transition: all 0.3s ease-out;
        }
      `;
      document.head.appendChild(style);
      
      skillGroups.forEach(group => {
        const skillTags = group.querySelectorAll('.skill-tag');
        skillTags.forEach(tag => {
          tag.style.opacity = '0';
          tag.style.transform = 'translateY(10px)';
        });
        
        observer.observe(group);
      });
    }
    
    // Initialize Experience Items Animation
    function initExperienceAnimation() {
      const experienceItems = document.querySelectorAll('.experience-item');
      
      if (experienceItems.length === 0) return;
      
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.2 });
      
      // Add CSS for animation
      const style = document.createElement('style');
      style.textContent = `
        .experience-item {
          opacity: 0;
          transform: translateY(20px);
          transition: all 0.8s ease-out;
        }
        
        .experience-item.revealed {
          opacity: 1;
          transform: translateY(0);
        }
      `;
      document.head.appendChild(style);
      
      experienceItems.forEach(item => {
        observer.observe(item);
      });
    }
    
    // Initialize Education Items Animation
    function initEducationAnimation() {
      const educationItems = document.querySelectorAll('.education-item');
      
      if (educationItems.length === 0) return;
      
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.2 });
      
      // Add CSS for animation
      const style = document.createElement('style');
      style.textContent = `
        .education-item {
          opacity: 0;
          transform: translateY(20px);
          transition: all 0.8s ease-out;
        }
        
        .education-item.revealed {
          opacity: 1;
          transform: translateY(0);
        }
      `;
      document.head.appendChild(style);
      
      educationItems.forEach(item => {
        observer.observe(item);
      });
    }
    
    /**
     * core/static/core/js/error.js
     * JavaScript for error pages
     */
    
    document.addEventListener('DOMContentLoaded', function() {
      // ===== TERMINAL ANIMATION =====
      initTerminalAnimation();
    });
    
    // Initialize Terminal Animation
    function initTerminalAnimation() {
      const terminalLines = document.querySelectorAll('.terminal-line');
      const terminalOutputs = document.querySelectorAll('.terminal-output');
      
      if (terminalLines.length === 0 || terminalOutputs.length === 0) return;
      
      // Hide all lines and outputs initially
      terminalLines.forEach(line => line.style.opacity = '0');
      terminalOutputs.forEach(output => output.style.opacity = '0');
      
      // Store original content for typing effect
      const originalLines = Array.from(terminalLines).map(line => line.textContent);
      
      // Clear all text content
      terminalLines.forEach(line => line.textContent = '');
      
      // Function to simulate typing text
      function typeText(element, text, index, speed, callback) {
        if (index < text.length) {
          element.textContent = text.substring(0, index + 1);
          setTimeout(() => {
            typeText(element, text, index + 1, speed, callback);
          }, speed);
        } else if (callback) {
          callback();
        }
      }
      
      // Animation sequence
      function animateSequence(lineIndex = 0) {
        if (lineIndex >= terminalLines.length) return;
        
        const line = terminalLines[lineIndex];
        const output = terminalOutputs[lineIndex];
        const text = originalLines[lineIndex];
        
        // Show line and animate typing
        line.style.opacity = '1';
        
        typeText(line, text, 0, 50, () => {
          // After line is typed, show output after a delay
          if (output) {
            setTimeout(() => {
              output.style.opacity = '1';
              
              // Move to next line
              setTimeout(() => {
                animateSequence(lineIndex + 1);
              }, 800);
            }, 500);
          } else {
            // If no output, move to next line
            setTimeout(() => {
              animateSequence(lineIndex + 1);
            }, 300);
          }
        });
      }
      
      // Start animation after short delay
      setTimeout(() => {
        animateSequence();
      }, 800);
    }
    
    /**
     * core/static/core/js/page.js
     * JavaScript for dynamic pages
     */
    
    document.addEventListener('DOMContentLoaded', function() {
      // ===== CODE SYNTAX HIGHLIGHTING =====
      initCodeHighlighting();
      
      // ===== TABLE OF CONTENTS GENERATION =====
      initTableOfContents();
      
      // ===== LIGHTBOX FOR IMAGES =====
      initImageLightbox();
    });
    
    // Initialize Code Syntax Highlighting
    function initCodeHighlighting() {
      // Check if Prism.js is available
      if (typeof Prism !== 'undefined') {
        Prism.highlightAll();
      } else if (typeof hljs !== 'undefined') {
        // Or use highlight.js if available
        document.querySelectorAll('pre code').forEach(block => {
          hljs.highlightBlock(block);
        });
      } else {
        // Basic styling for code blocks if no syntax highlighter is available
        const style = document.createElement('style');
        style.textContent = `
          .page-content pre {
            background-color: rgba(10, 10, 26, 0.7);
            padding: 1.5rem;
            border-radius: var(--border-radius-md);
            overflow-x: auto;
            margin: 1.5rem 0;
            font-family: var(--font-code);
            font-size: 0.9rem;
            line-height: 1.4;
          }
          
          .page-content code {
            background-color: rgba(10, 10, 26, 0.7);
            padding: 0.2rem 0.4rem;
            border-radius: var(--border-radius-sm);
            font-family: var(--font-code);
            font-size: 0.9rem;
            color: var(--color-cyan);
          }
        `;
        document.head.appendChild(style);
      }
    }
    
    // Initialize Table of Contents Generation
    function initTableOfContents() {
      const pageContent = document.querySelector('.page-content');
      if (!pageContent) return;
      
      // Find all headings in the content
      const headings = pageContent.querySelectorAll('h2, h3');
      if (headings.length < 3) return; // Don't generate TOC for few headings
      
      // Create TOC container
      const tocContainer = document.createElement('div');
      tocContainer.className = 'toc-container';
      tocContainer.innerHTML = '<h2 class="toc-title">Table of Contents</h2>';
      
      // Create TOC list
      const tocList = document.createElement('ul');
      tocList.className = 'toc-list';
      
      // Process headings
      headings.forEach(heading => {
        // Add ID to heading if not exists
        if (!heading.id) {
          heading.id = heading.textContent.toLowerCase().replace(/[^\w]+/g, '-');
        }
        
        // Create TOC item
        const tocItem = document.createElement('li');
        tocItem.className = `toc-item level-${heading.tagName.toLowerCase()}`;
        
        const tocLink = document.createElement('a');
        tocLink.href = `#${heading.id}`;
        tocLink.className = 'toc-link';
        tocLink.textContent = heading.textContent;
        
        tocItem.appendChild(tocLink);
        tocList.appendChild(tocItem);
        
        // Add click event for smooth scrolling
        tocLink.addEventListener('click', function(e) {
          e.preventDefault();
          
          const targetElement = document.getElementById(heading.id);
          if (targetElement) {
            // Get header height for offset
            const headerHeight = document.querySelector('.site-header')?.offsetHeight || 80;
            
            window.scrollTo({
              top: targetElement.offsetTop - headerHeight - 20,
              behavior: 'smooth'
            });
            
            // Update URL hash
            history.pushState(null, null, `#${heading.id}`);
          }
        });
      });
      
      tocContainer.appendChild(tocList);
      
      // Insert TOC before content
      const firstParagraph = pageContent.querySelector('p');
      if (firstParagraph) {
        pageContent.insertBefore(tocContainer, firstParagraph);
      } else {
        pageContent.prepend(tocContainer);
      }
      
      // Add CSS for TOC
      const style = document.createElement('style');
      style.textContent = `
        .toc-container {
          background-color: rgba(18, 18, 24, 0.7);
          border: 1px solid rgba(0, 240, 255, 0.1);
          border-radius: var(--border-radius-md);
          padding: 1.5rem;
          margin-bottom: 2rem;
        }
        
        .toc-title {
          font-family: var(--font-heading);
          font-size: 1.3rem;
          color: var(--color-cyan);
          margin-bottom: 1rem;
          padding-bottom: 0.5rem;
          border-bottom: 1px solid rgba(0, 240, 255, 0.2);
        }
        
        .toc-list {
          list-style: none;
          padding-left: 0;
        }
        
        .toc-list li {
          margin-bottom: 0.5rem;
        }
        
        .toc-list .level-h3 {
          padding-left: 1.5rem;
        }
        
        .toc-link {
          color: var(--color-text-secondary);
          text-decoration: none;
          transition: all 0.3s ease;
          display: inline-block;
          padding: 0.2rem 0;
        }
        
        .toc-link:hover {
          color: var(--color-cyan);
          transform: translateX(3px);
        }
        
        .toc-link.active {
          color: var(--color-cyan);
        }
      `;
      document.head.appendChild(style);
      
      // Highlight active TOC item on scroll
      window.addEventListener('scroll', function() {
        const scrollPosition = window.scrollY + 100; // Add offset for header
        
        // Find the current section
        let currentSection = null;
        
        headings.forEach(heading => {
          if (heading.offsetTop <= scrollPosition) {
            currentSection = heading.id;
          }
        });
        
        // Highlight the corresponding TOC link
        if (currentSection) {
          // Remove active class from all links
          document.querySelectorAll('.toc-link').forEach(link => {
            link.classList.remove('active');
          });
          
          // Add active class to current link
          const activeLink = document.querySelector(`.toc-link[href="#${currentSection}"]`);
          if (activeLink) {
            activeLink.classList.add('active');
          }
        }
      });
    }
    
    // Initialize Image Lightbox
    function initImageLightbox() {
      const pageContent = document.querySelector('.page-content');
      if (!pageContent) return;
      
      // Find all images in the content
      const images = pageContent.querySelectorAll('img');
      if (images.length === 0) return;
      
      // Add lightbox functionality
      images.forEach(image => {
        // Make images clickable
        image.style.cursor = 'pointer';
        
        // Add click event
        image.addEventListener('click', function() {
          // Create lightbox container
          const lightbox = document.createElement('div');
          lightbox.className = 'lightbox';
          
          // Create lightbox content
          const lightboxContent = document.createElement('div');
          lightboxContent.className = 'lightbox-content';
          
          // Create close button
          const closeButton = document.createElement('button');
          closeButton.className = 'lightbox-close';
          closeButton.innerHTML = '&times;';
          
          // Create image element
          const lightboxImage = document.createElement('img');
          lightboxImage.src = this.src;
          lightboxImage.alt = this.alt;
          
          // Create caption
          const caption = document.createElement('div');
          caption.className = 'lightbox-caption';
          caption.textContent = this.alt || 'Image';
          
          // Append elements
          lightboxContent.appendChild(closeButton);
          lightboxContent.appendChild(lightboxImage);
          lightboxContent.appendChild(caption);
          lightbox.appendChild(lightboxContent);
          document.body.appendChild(lightbox);
          
          // Show lightbox with animation
          setTimeout(() => {
            lightbox.style.opacity = '1';
          }, 10);
          
          // Close on button click
          closeButton.addEventListener('click', function() {
            lightbox.style.opacity = '0';
            setTimeout(() => {
              document.body.removeChild(lightbox);
            }, 300);
          });
          
          // Close on outside click
          lightbox.addEventListener('click', function(e) {
            if (e.target === lightbox) {
              lightbox.style.opacity = '0';
              setTimeout(() => {
                document.body.removeChild(lightbox);
              }, 300);
            }
          });
        });
      });
      
      // Add CSS for lightbox
      const style = document.createElement('style');
      style.textContent = `
        .lightbox {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background-color: rgba(0, 0, 0, 0.9);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 9999;
          opacity: 0;
          transition: opacity 0.3s ease;
        }
        
        .lightbox-content {
          position: relative;
          max-width: 90%;
          max-height: 90%;
          background-color: rgba(18, 18, 24, 0.9);
          padding: 1rem;
          border-radius: var(--border-radius-md);
          border: 1px solid rgba(0, 240, 255, 0.2);
        }
        
        .lightbox-close {
          position: absolute;
          top: -15px;
          right: -15px;
          width: 30px;
          height: 30px;
          background-color: rgba(0, 240, 255, 0.2);
          color: var(--color-text);
          border: 1px solid rgba(0, 240, 255, 0.4);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.5rem;
          cursor: pointer;
          z-index: 1;
          transition: all 0.3s ease;
        }
        
        .lightbox-close:hover {
          background-color: rgba(0, 240, 255, 0.4);
          transform: rotate(90deg);
        }
        
        .lightbox-content img {
          display: block;
          max-width: 100%;
          max-height: 80vh;
          margin: 0 auto;
          border-radius: var(--border-radius-sm);
        }
        
        .lightbox-caption {
          text-align: center;
          padding: 1rem 0 0;
          color: var(--color-text-secondary);
          font-size: 0.9rem;
        }
      `;
      document.head.appendChild(style);
    }