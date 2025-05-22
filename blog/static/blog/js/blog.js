/**
 * ML DEVLOG - Blog/DEVLOG JavaScript
 * Interactive functionality for the blog section
 * Version: 1.1.0
 */

document.addEventListener('DOMContentLoaded', function() {
  // ===== INITIALIZE ALL BLOG FUNCTIONALITY =====
  initBlogFilters();
  initCodeBlocks();
  initReadingProgress();
  initTableOfContents();
  initSearchPanel();
  initCategoryHexagons();
  initPostCards();
  initCommentForm();
  initTimelineNavigation();
  initAnimations();
});

// ===== BLOG FILTER FUNCTIONALITY =====
function initBlogFilters() {
  const filterOptions = document.querySelectorAll('.filter-option');
  const filterDropdown = document.querySelector('.sort-dropdown');
  
  // Handle click filters
  filterOptions.forEach(option => {
    option.addEventListener('click', function(e) {
      e.preventDefault();
      
      // Remove active class from all filters
      filterOptions.forEach(opt => opt.classList.remove('active'));
      
      // Add active class to clicked filter
      this.classList.add('active');
      
      // Get filter value from data attribute
      const filterValue = this.dataset.filter;
      filterPosts(filterValue);
    });
  });
  
  // Handle dropdown sorting
  if (filterDropdown) {
    filterDropdown.addEventListener('change', function() {
      const url = this.value;
      if (url) {
        window.location.href = url;
      }
    });
  }
  
  // Filter posts function
  function filterPosts(filterValue) {
    const postCards = document.querySelectorAll('.post-card');
    
    if (filterValue === 'all') {
      // Show all posts
      postCards.forEach(card => {
        card.style.display = 'block';
        setTimeout(() => {
          card.style.opacity = '1';
          card.style.transform = 'translateY(0)';
        }, 50);
      });
    } else {
      // Filter posts by category/tag
      postCards.forEach(card => {
        const cardCategory = card.dataset.category;
        const cardTags = card.dataset.tags ? card.dataset.tags.split(',') : [];
        
        if (cardCategory === filterValue || cardTags.includes(filterValue)) {
          card.style.display = 'block';
          setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
          }, 50);
        } else {
          card.style.opacity = '0';
          card.style.transform = 'translateY(20px)';
          setTimeout(() => {
            card.style.display = 'none';
          }, 300);
        }
      });
    }
  }
}

// ===== CODE BLOCK FUNCTIONALITY =====
function initCodeBlocks() {
  const codeBlocks = document.querySelectorAll('.code-block');
  
  codeBlocks.forEach(block => {
    const header = block.querySelector('.code-header');
    
    // Skip if already initialized
    if (header && !header.querySelector('.copy-button')) {
      // Add copy button
      const copyBtn = document.createElement('button');
      copyBtn.className = 'copy-button';
      copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
      copyBtn.title = 'Copy code';
      copyBtn.style.background = 'transparent';
      copyBtn.style.border = 'none';
      copyBtn.style.color = '#808080';
      copyBtn.style.cursor = 'pointer';
      copyBtn.style.marginLeft = 'auto';
      header.appendChild(copyBtn);
      
      // Click handler for copy button
      copyBtn.addEventListener('click', () => {
        const codeContent = block.querySelector('.code-content');
        const code = codeContent.querySelector('code') || codeContent.querySelector('pre');
        const textToCopy = code ? code.textContent : codeContent.textContent;
        
        navigator.clipboard.writeText(textToCopy)
          .then(() => {
            // Success state
            copyBtn.innerHTML = '<i class="fas fa-check"></i>';
            copyBtn.style.color = '#27c93f';
            setTimeout(() => {
              copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
              copyBtn.style.color = '#808080';
            }, 2000);
          })
          .catch(() => {
            // Error state
            copyBtn.innerHTML = '<i class="fas fa-times"></i>';
            copyBtn.style.color = '#ff5f56';
            setTimeout(() => {
              copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
              copyBtn.style.color = '#808080';
            }, 2000);
          });
      });
    }
  });
  
  // Initialize syntax highlighting if library is available
  if (typeof Prism !== 'undefined') {
    Prism.highlightAll();
  } else if (typeof hljs !== 'undefined') {
    document.querySelectorAll('pre code').forEach(block => {
      hljs.highlightBlock(block);
    });
  }
}

// ===== READING PROGRESS BAR =====
function initReadingProgress() {
  const progressBar = document.querySelector('.reading-progress-bar');
  const postContent = document.querySelector('.post-content');
  
  if (progressBar && postContent) {
    // Initial calculation
    updateReadingProgress();
    
    // Update on scroll
    window.addEventListener('scroll', updateReadingProgress);
    
    // Update on window resize
    window.addEventListener('resize', updateReadingProgress);
    
    function updateReadingProgress() {
      // Calculate how far down the page the user has scrolled
      const scrollTop = window.scrollY || document.documentElement.scrollTop;
      const postStart = postContent.offsetTop;
      const postHeight = postContent.offsetHeight;
      const windowHeight = window.innerHeight;
      
      // Calculate scroll percentage
      let scrollPercent = 0;
      if (scrollTop > postStart) {
        const scrollDistance = scrollTop - postStart;
        const readableHeight = postHeight - windowHeight;
        scrollPercent = (scrollDistance / readableHeight) * 100;
      }
      
      // Limit percentage to 0-100
      scrollPercent = Math.min(100, Math.max(0, scrollPercent));
      
      // Update progress bar width
      progressBar.style.width = `${scrollPercent}%`;
    }
  }
}

// ===== TABLE OF CONTENTS FUNCTIONALITY =====
function initTableOfContents() {
  const tocLinks = document.querySelectorAll('.toc-list-item a');
  const headings = document.querySelectorAll('.post-content h2, .post-content h3');
  
  if (tocLinks.length > 0 && headings.length > 0) {
    // Smooth scroll to heading when TOC link is clicked
    tocLinks.forEach(link => {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        const targetElement = document.querySelector(targetId);
        
        if (targetElement) {
          // Calculate position considering fixed header
          const headerHeight = document.querySelector('.navbar')?.offsetHeight || 0;
          const targetPosition = targetElement.getBoundingClientRect().top + window.scrollY;
          
          // Scroll to element
          window.scrollTo({
            top: targetPosition - headerHeight - 20,
            behavior: 'smooth'
          });
          
          // Update URL hash without scrolling
          history.pushState(null, null, targetId);
        }
      });
    });
    
    // Highlight active TOC items on scroll
    window.addEventListener('scroll', function() {
      // Get current scroll position
      const scrollPosition = window.scrollY + 100; // Offset for header
      
      // Find the current section
      let currentSection = null;
      
      headings.forEach(heading => {
        // Get heading position
        const headingPosition = heading.getBoundingClientRect().top + window.scrollY;
        
        // Check if heading is above current scroll position
        if (headingPosition <= scrollPosition) {
          currentSection = heading.id;
        }
      });
      
      // Remove active class from all TOC links
      tocLinks.forEach(link => {
        link.classList.remove('active');
      });
      
      // Add active class to the link that corresponds to current section
      if (currentSection) {
        const activeLink = document.querySelector(`.toc-list-item a[href="#${currentSection}"]`);
        if (activeLink) {
          activeLink.classList.add('active');
        }
      }
    });
  }
}

// ===== SEARCH PANEL FUNCTIONALITY =====
function initSearchPanel() {
  const searchToggle = document.getElementById('search-toggle');
  const searchPanel = document.getElementById('search-panel');
  
  if (searchToggle && searchPanel) {
    // Toggle search panel visibility
    searchToggle.addEventListener('click', function(e) {
      e.preventDefault();
      
      // Toggle panel
      if (searchPanel.style.display === 'none' || !searchPanel.style.display) {
        searchPanel.style.display = 'block';
        
        // Add animation class
        searchPanel.classList.add('fade-in');
        
        // Focus search input
        setTimeout(() => {
          const searchInput = searchPanel.querySelector('input');
          if (searchInput) {
            searchInput.focus();
          }
        }, 100);
      } else {
        // Add fade out class
        searchPanel.classList.add('fade-out');
        
        // Hide panel after animation completes
        setTimeout(() => {
          searchPanel.style.display = 'none';
          searchPanel.classList.remove('fade-out');
        }, 300);
      }
    });
    
    // Close search panel when clicking outside
    document.addEventListener('click', function(e) {
      if (searchPanel.style.display === 'block' && 
          !searchPanel.contains(e.target) && 
          !searchToggle.contains(e.target)) {
        
        // Add fade out class
        searchPanel.classList.add('fade-out');
        
        // Hide panel after animation completes
        setTimeout(() => {
          searchPanel.style.display = 'none';
          searchPanel.classList.remove('fade-out');
        }, 300);
      }
    });
    
    // Handle search form submission (if not using GET method)
    const searchForm = searchPanel.querySelector('form');
    if (searchForm && searchForm.getAttribute('method') !== 'get') {
      searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const searchInput = this.querySelector('input');
        const searchQuery = searchInput.value.trim();
        
        if (searchQuery) {
          // Redirect to search page
          window.location.href = `/blog/search/?q=${encodeURIComponent(searchQuery)}`;
        }
      });
    }
  }
}

// ===== CATEGORY HEXAGONS FUNCTIONALITY =====
function initCategoryHexagons() {
  const hexagons = document.querySelectorAll('.category-hex');
  
  hexagons.forEach(hex => {
    // Add hover effects
    hex.addEventListener('mouseenter', function() {
      // Get category color from CSS variable or data attribute
      const categoryColor = getComputedStyle(this).getPropertyValue('--category-color').trim() || 
                          this.dataset.color || 
                          '#00f0ff';
      
      // Add glow effect
      this.style.filter = `drop-shadow(0 0 8px ${categoryColor})`;
      this.style.transform = 'scale(1.1)';
      
      // Update category name color if present
      const nameElement = this.closest('.category-item')?.querySelector('.category-name');
      if (nameElement) {
        nameElement.style.color = categoryColor;
      }
    });
    
    hex.addEventListener('mouseleave', function() {
      // Remove effects
      this.style.filter = '';
      this.style.transform = '';
      
      // Reset category name color
      const nameElement = this.closest('.category-item')?.querySelector('.category-name');
      if (nameElement) {
        nameElement.style.color = '';
      }
    });
  });
}

// ===== POST CARDS FUNCTIONALITY =====
function initPostCards() {
  const postCards = document.querySelectorAll('.post-card');
  
  postCards.forEach(card => {
    // Add hover interactions
    card.addEventListener('mouseenter', function() {
      // Enhance image
      const image = this.querySelector('.post-card-image img');
      if (image) {
        image.style.transform = 'scale(1.05)';
      }
      
      // Animate link arrow
      const arrow = this.querySelector('.post-link .arrow');
      if (arrow) {
        arrow.style.transform = 'translateX(5px)';
      }
    });
    
    card.addEventListener('mouseleave', function() {
      // Reset image
      const image = this.querySelector('.post-card-image img');
      if (image) {
        image.style.transform = '';
      }
      
      // Reset link arrow
      const arrow = this.querySelector('.post-link .arrow');
      if (arrow) {
        arrow.style.transform = '';
      }
    });
  });
}

// ===== COMMENT FORM FUNCTIONALITY =====
function initCommentForm() {
  const commentForm = document.querySelector('.comment-form');
  
  if (commentForm) {
    // Form validation
    commentForm.addEventListener('submit', function(e) {
      let hasError = false;
      
      // Get required fields
      const requiredFields = this.querySelectorAll('[required]');
      
      requiredFields.forEach(field => {
        // Remove existing error messages
        const existingError = field.parentNode.querySelector('.error-message');
        if (existingError) {
          existingError.remove();
        }
        
        // Remove error styles
        field.classList.remove('error');
        
        // Check if field is empty
        if (!field.value.trim()) {
          e.preventDefault();
          hasError = true;
          
          // Add error class
          field.classList.add('error');
          
          // Add error message
          const errorMessage = document.createElement('div');
          errorMessage.className = 'error-message';
          errorMessage.textContent = `${field.getAttribute('placeholder') || 'This field'} is required`;
          
          // Insert after field
          field.parentNode.insertBefore(errorMessage, field.nextSibling);
        }
      });
      
      // Email validation if present
      const emailField = this.querySelector('input[type="email"]');
      if (emailField && emailField.value.trim()) {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (!emailPattern.test(emailField.value.trim())) {
          e.preventDefault();
          hasError = true;
          
          // Add error class
          emailField.classList.add('error');
          
          // Add error message if not already present
          if (!emailField.parentNode.querySelector('.error-message')) {
            const errorMessage = document.createElement('div');
            errorMessage.className = 'error-message';
            errorMessage.textContent = 'Please enter a valid email address';
            
            // Insert after field
            emailField.parentNode.insertBefore(errorMessage, emailField.nextSibling);
          }
        }
      }
      
      // If no errors, show loading state
      if (!hasError) {
        const submitButton = this.querySelector('button[type="submit"]');
        if (submitButton) {
          submitButton.disabled = true;
          submitButton.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Submitting...';
        }
      }
    });
    
    // Clear error styling on input
    const formInputs = commentForm.querySelectorAll('input, textarea');
    formInputs.forEach(input => {
      input.addEventListener('input', function() {
        // Remove error class
        this.classList.remove('error');
        
        // Remove error message
        const errorMessage = this.parentNode.querySelector('.error-message');
        if (errorMessage) {
          errorMessage.remove();
        }
      });
    });
  }
  
  // Initialize comment reply functionality
  const replyButtons = document.querySelectorAll('.comment-reply');
  replyButtons.forEach(button => {
    button.addEventListener('click', function() {
      // Get comment ID
      const commentId = this.dataset.commentId;
      
      // Move comment form after clicked comment
      if (commentId && commentForm) {
        const targetComment = document.getElementById(`comment-${commentId}`);
        if (targetComment) {
          // Clone form if necessary
          const formClone = commentForm.cloneNode(true);
          formClone.classList.add('reply-form');
          
          // Add hidden field for parent comment
          const parentField = document.createElement('input');
          parentField.type = 'hidden';
          parentField.name = 'parent_id';
          parentField.value = commentId;
          formClone.appendChild(parentField);
          
          // Add cancel button
          const cancelButton = document.createElement('button');
          cancelButton.type = 'button';
          cancelButton.className = 'btn-cancel-reply';
          cancelButton.innerHTML = 'Cancel Reply';
          
          const submitButton = formClone.querySelector('button[type="submit"]');
          if (submitButton) {
            submitButton.parentNode.insertBefore(cancelButton, submitButton);
          } else {
            formClone.appendChild(cancelButton);
          }
          
          // Cancel reply handler
          cancelButton.addEventListener('click', function() {
            formClone.remove();
          });
          
          // Insert form after comment
          targetComment.after(formClone);
          
          // Focus on first field
          const firstInput = formClone.querySelector('input, textarea');
          if (firstInput) {
            firstInput.focus();
          }
        }
      }
    });
  });
}

// ===== TIMELINE NAVIGATION FUNCTIONALITY =====
function initTimelineNavigation() {
  const archivePage = document.querySelector('.time-navigator');
  
  if (archivePage) {
    // Handle year selection
    const yearItems = document.querySelectorAll('.year-block');
    const monthsContainer = document.querySelector('.months-section');
    
    yearItems.forEach(item => {
      item.addEventListener('click', function(e) {
        // If link, let default behavior handle it
        if (this.tagName === 'A') {
          return;
        }
        
        e.preventDefault();
        
        // Remove active class from all years
        yearItems.forEach(year => year.classList.remove('active'));
        
        // Add active class to clicked year
        this.classList.add('active');
        
        // Get year value
        const year = this.dataset.year;
        
        // Show months for selected year
        if (monthsContainer) {
          // Trigger months loading animation
          monthsContainer.classList.add('loading');
          
          // Simulated delay for animation effect
          setTimeout(() => {
            // Remove loading state
            monthsContainer.classList.remove('loading');
            
            // Update months visibility based on selected year
            const monthItems = document.querySelectorAll('.month-block');
            monthItems.forEach(month => {
              if (month.dataset.year === year) {
                month.style.display = 'block';
              } else {
                month.style.display = 'none';
              }
            });
          }, 300);
        }
      });
    });
    
    // Handle month selection
    const monthItems = document.querySelectorAll('.month-block');
    
    monthItems.forEach(item => {
      item.addEventListener('click', function(e) {
        // If link, let default behavior handle it
        if (this.tagName === 'A') {
          return;
        }
        
        e.preventDefault();
        
        // Remove active class from all months
        monthItems.forEach(month => month.classList.remove('active'));
        
        // Add active class to clicked month
        this.classList.add('active');
        
        // Get year and month values
        const year = this.dataset.year;
        const month = this.dataset.month;
        
        // Redirect to archive page for selected year/month
        if (year && month) {
          window.location.href = `/blog/archive/${year}/${month}/`;
        }
      });
    });
    
    // Scan line animation
    const timelineScanLine = document.querySelector('.timeline-scan-line');
    if (timelineScanLine) {
      // Add scan animation
      startTimelineScan(timelineScanLine);
    }
  }
}

// Function to start timeline scan animation
function startTimelineScan(element) {
  // Set initial position
  element.style.top = '30px';
  element.style.opacity = '0';
  
  // Animation function
  function animateScan() {
    // Reset position
    element.style.top = '30px';
    element.style.opacity = '0';
    
    // Force reflow
    element.offsetHeight;
    
    // Add animation
    element.style.transition = 'transform 3s linear, opacity 0.3s ease-in-out';
    element.style.opacity = '0.6';
    element.style.transform = 'translateY(100px)';
    
    // Reset after animation completes
    setTimeout(() => {
      element.style.transition = 'none';
      element.style.transform = 'translateY(0)';
      element.style.opacity = '0';
      
      // Start next animation
      setTimeout(animateScan, 500);
    }, 3000);
  }
  
  // Start animation
  animateScan();
}

// ===== ANIMATIONS ===== 
function initAnimations() {
  // Featured post scanning effect
  const featuredPost = document.querySelector('.featured-post');
  if (featuredPost) {
    const scanLine = document.createElement('div');
    scanLine.className = 'scan-line';
    featuredPost.appendChild(scanLine);
    
    // Start scan animation
    animateScanLine(scanLine);
  }
  
  // Matrix data visualization on categories
  const categoriesSection = document.querySelector('.categories-section');
  if (categoriesSection) {
    initMatrixBackground(categoriesSection);
  }
  
  // Typing animation for headings
  const typingElements = document.querySelectorAll('.typing-animation');
  typingElements.forEach(element => {
    initTypingAnimation(element);
  });
  
  // Smooth reveal on scroll for cards
  const postCards = document.querySelectorAll('.post-card');
  if (postCards.length > 0) {
    // Create intersection observer
    const cardObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          // Add animation class when card comes into view
          entry.target.classList.add('fade-in-up');
          // Unobserve after animation has been triggered
          cardObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    
    // Observe each card
    postCards.forEach(card => {
      // Remove any existing animation classes
      card.classList.remove('fade-in-up');
      // Add initial invisible state
      card.style.opacity = '0';
      card.style.transform = 'translateY(20px)';
      // Observe card
      cardObserver.observe(card);
    });
  }
}

// Function to animate scan line
function animateScanLine(element) {
  // Animation properties
  const duration = 3000;
  const interval = 5000;
  
  // Animation function
  function animate() {
    // Start position (offscreen top)
    element.style.top = '-5px';
    element.style.opacity = '0';
    
    // Force reflow
    element.offsetHeight;
    
    // Start animation
    element.style.transition = `top ${duration}ms linear, opacity 300ms ease-in-out`;
    element.style.top = '105%';
    element.style.opacity = '0.6';
    
    // Reset after animation completes
    setTimeout(() => {
      element.style.transition = 'none';
      element.style.opacity = '0';
      
      // Schedule next animation
      setTimeout(animate, 1000);
    }, duration);
  }
  
  // Start animation
  animate();
}

// Function to initialize matrix background
function initMatrixBackground(container) {
  // Create canvas element
  const canvas = document.createElement('canvas');
  canvas.className = 'matrix-canvas';
  canvas.style.position = 'absolute';
  canvas.style.top = '0';
  canvas.style.left = '0';
  canvas.style.width = '100%';
  canvas.style.height = '100%';
  canvas.style.zIndex = '-1';
  canvas.style.opacity = '0.05';
  
  // Insert canvas as first child
  container.style.position = 'relative';
  container.insertBefore(canvas, container.firstChild);
  
  // Set canvas size
  const resize = () => {
    canvas.width = container.offsetWidth;
    canvas.height = container.offsetHeight;
    
    // Restart animation
    if (animationId) {
      cancelAnimationFrame(animationId);
      startMatrix();
    }
  };
  
  // Initial size
  resize();
  
  // Resize on window resize
  window.addEventListener('resize', debounce(resize, 250));
  
  // Matrix animation
  const ctx = canvas.getContext('2d');
  let columns;
  let drops;
  let animationId;
  
  // Characters
  const characters = '01';
  
  function startMatrix() {
    // Calculate columns
    const fontSize = 10;
    columns = Math.floor(canvas.width / fontSize);
    
    // Initialize drops
    drops = [];
    for (let i = 0; i < columns; i++) {
      drops[i] = Math.random() * -100;
    }
    
    // Animation loop
    function draw() {
      // Semi-transparent black background for trailing effect
      ctx.fillStyle = 'rgba(10, 10, 26, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // Text style
      ctx.fillStyle = '#00f0ff';
      ctx.font = `${fontSize}px monospace`;
      
      // Draw characters
      for (let i = 0; i < drops.length; i++) {
        // Random character
        const text = characters.charAt(Math.floor(Math.random() * characters.length));
        
        // x coordinate of the drop
        const x = i * fontSize;
        
        // y coordinate of the drop
        const y = drops[i] * fontSize;
        
        // Draw the character
        ctx.fillText(text, x, y);
        
        // Send the drop back to the top randomly after it crosses the screen
        if (y > canvas.height && Math.random() > 0.99) {
          drops[i] = 0;
        }
        
        // Move drops down
        drops[i]++;
      }
      
      // Request next frame
      animationId = requestAnimationFrame(draw);
    }
    
    // Start animation
    draw();
  }
  
  // Start animation
  startMatrix();
}

// Function to initialize typing animation
function initTypingAnimation(element) {
  // Get original text
  const originalText = element.textContent;
  
  // Clear text initially
  element.textContent = '';
  
  // Set typing delay
  const typingDelay = 100;
  
  // Type text character by character
  let i = 0;
  
  function typeChar() {
    if (i < originalText.length) {
      element.textContent += originalText.charAt(i);
      i++;
      setTimeout(typeChar, typingDelay);
    } else {
      // Typing complete
      // Wait a bit before starting over
      setTimeout(() => {
        // Clear text
        element.textContent = '';
        // Reset counter
        i = 0;
        // Start typing again
        setTimeout(typeChar, typingDelay);
      }, 5000);
    }
  }
  
  // Start typing after a short delay
  setTimeout(typeChar, 1000);
}

// ===== UTILITY FUNCTIONS =====
// Debounce function to limit how often a function is executed
function debounce(func, delay) {
  let timeout;
  return function() {
    const context = this;
    const args = arguments;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), delay);
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

// Get query parameter from URL
function getQueryParam(param) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(param);
}

// Format date string
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

// Generate random number between min and max
function randomBetween(min, max) {
  return Math.random() * (max - min) + min;
}

// Check if element is in viewport
function isInViewport(element) {
  const rect = element.getBoundingClientRect();
  return (
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
  );
}

// AJAX utility function for making requests
function ajaxRequest(url, method = 'GET', data = null) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url);
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    
    if (data && !(data instanceof FormData)) {
      xhr.setRequestHeader('Content-Type', 'application/json');
    }
    
    xhr.onload = function() {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText);
          resolve(response);
        } catch (e) {
          resolve(xhr.responseText);
        }
      } else {
        reject({
          status: xhr.status,
          statusText: xhr.statusText,
          response: xhr.responseText
        });
      }
    };
    
    xhr.onerror = function() {
      reject({
        status: xhr.status,
        statusText: xhr.statusText,
        response: xhr.responseText
      });
    };
    
    // Send the request
    if (data instanceof FormData) {
      xhr.send(data);
    } else if (data) {
      xhr.send(JSON.stringify(data));
    } else {
      xhr.send();
    }
  });
}

// ===== DATA VISUALIZATION COMPONENTS =====
// These components add advanced data visualization features to the blog

// Generate skill radar chart
function generateSkillRadarChart(container, skills) {
  // Skills should be an array of objects with name, value, and max properties
  if (!container || !skills || !skills.length) return;
  
  // Set container positioning
  container.style.position = 'relative';
  
  // Create SVG element
  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("width", "100%");
  svg.setAttribute("height", "100%");
  svg.setAttribute("viewBox", "0 0 200 200");
  container.appendChild(svg);
  
  // Center coordinates
  const centerX = 100;
  const centerY = 100;
  const radius = 80;
  
  // Calculate number of skills and angle step
  const numSkills = skills.length;
  const angleStep = (2 * Math.PI) / numSkills;
  
  // Add background rings
  for (let i = 1; i <= 5; i++) {
    const ring = document.createElementNS(svgNS, "circle");
    ring.setAttribute("cx", centerX);
    ring.setAttribute("cy", centerY);
    ring.setAttribute("r", radius * (i/5));
    ring.setAttribute("fill", "none");
    ring.setAttribute("stroke", "rgba(0, 240, 255, 0.1)");
    ring.setAttribute("stroke-width", "1");
    svg.appendChild(ring);
  }
  
  // Add axes
  skills.forEach((skill, i) => {
    const angle = i * angleStep - Math.PI/2; // Start from top
    const axisX = centerX + radius * Math.cos(angle);
    const axisY = centerY + radius * Math.sin(angle);
    
    // Draw axis line
    const axis = document.createElementNS(svgNS, "line");
    axis.setAttribute("x1", centerX);
    axis.setAttribute("y1", centerY);
    axis.setAttribute("x2", axisX);
    axis.setAttribute("y2", axisY);
    axis.setAttribute("stroke", "rgba(0, 240, 255, 0.2)");
    axis.setAttribute("stroke-width", "1");
    svg.appendChild(axis);
    
    // Add label
    const labelRadius = radius + 20;
    const labelX = centerX + labelRadius * Math.cos(angle);
    const labelY = centerY + labelRadius * Math.sin(angle);
    
    const label = document.createElementNS(svgNS, "text");
    label.setAttribute("x", labelX);
    label.setAttribute("y", labelY);
    label.setAttribute("text-anchor", "middle");
    label.setAttribute("fill", "var(--color-text-secondary)");
    label.setAttribute("font-size", "10");
    label.setAttribute("font-family", "var(--font-body)");
    label.textContent = skill.name;
    svg.appendChild(label);
  });
  
  // Calculate polygon points
  const points = skills.map((skill, i) => {
    const angle = i * angleStep - Math.PI/2;
    const value = skill.value / skill.max;
    const pointRadius = radius * value;
    
    return {
      x: centerX + pointRadius * Math.cos(angle),
      y: centerY + pointRadius * Math.sin(angle),
      value: skill.value
    };
  });
  
  // Draw data polygon with animation
  const polygon = document.createElementNS(svgNS, "polygon");
  polygon.setAttribute("fill", "rgba(0, 240, 255, 0.1)");
  polygon.setAttribute("stroke", "var(--color-cyan)");
  polygon.setAttribute("stroke-width", "2");
  svg.appendChild(polygon);
  
  // Add animation to the polygon
  function animatePolygon() {
    // Start with just center point
    let currentPoints = [];
    for (let i = 0; i < points.length; i++) {
      currentPoints.push(`${centerX},${centerY}`);
    }
    polygon.setAttribute("points", currentPoints.join(" "));
    
    // Animate to actual values
    let step = 0;
    const totalSteps = 20;
    
    function animateStep() {
      if (step <= totalSteps) {
        // Calculate intermediate points
        const intermediatePoints = points.map((point, i) => {
          const x = centerX + (point.x - centerX) * (step / totalSteps);
          const y = centerY + (point.y - centerY) * (step / totalSteps);
          return `${x},${y}`;
        });
        
        // Update polygon
        polygon.setAttribute("points", intermediatePoints.join(" "));
        
        // Next step
        step++;
        requestAnimationFrame(animateStep);
      } else {
        // Animation complete, add data points
        addDataPoints();
      }
    }
    
    // Start animation
    animateStep();
  }
  
  // Add data points
  function addDataPoints() {
    points.forEach((point, i) => {
      // Create data point
      const dataPoint = document.createElementNS(svgNS, "circle");
      dataPoint.setAttribute("cx", point.x);
      dataPoint.setAttribute("cy", point.y);
      dataPoint.setAttribute("r", "4");
      dataPoint.setAttribute("fill", "var(--color-cyan)");
      dataPoint.setAttribute("stroke", "var(--color-bg-primary)");
      dataPoint.setAttribute("stroke-width", "1");
      
      // Add tooltip with value
      dataPoint.setAttribute("data-value", skills[i].value);
      dataPoint.setAttribute("data-name", skills[i].name);
      
      // Add event listeners for tooltip
      dataPoint.addEventListener('mouseenter', showTooltip);
      dataPoint.addEventListener('mouseleave', hideTooltip);
      
      svg.appendChild(dataPoint);
    });
  }
  
  // Tooltip functionality
  let tooltip = null;
  
  function showTooltip(e) {
    const point = e.target;
    const name = point.getAttribute('data-name');
    const value = point.getAttribute('data-value');
    
    // Create tooltip
    tooltip = document.createElement('div');
    tooltip.className = 'skill-tooltip';
    tooltip.style.position = 'absolute';
    tooltip.style.backgroundColor = 'rgba(10, 10, 26, 0.9)';
    tooltip.style.color = 'var(--color-text)';
    tooltip.style.padding = '5px 10px';
    tooltip.style.borderRadius = '4px';
    tooltip.style.fontSize = '12px';
    tooltip.style.pointerEvents = 'none';
    tooltip.style.zIndex = '1000';
    tooltip.style.border = '1px solid var(--color-cyan)';
    tooltip.style.boxShadow = '0 0 10px rgba(0, 240, 255, 0.3)';
    tooltip.textContent = `${name}: ${value}`;
    
    // Position tooltip
    const rect = container.getBoundingClientRect();
    const pointRect = point.getBoundingClientRect();
    const tooltipX = pointRect.left - rect.left;
    const tooltipY = pointRect.top - rect.top - 30;
    
    tooltip.style.left = `${tooltipX}px`;
    tooltip.style.top = `${tooltipY}px`;
    
    // Add to container
    container.appendChild(tooltip);
  }
  
  function hideTooltip() {
    if (tooltip) {
      tooltip.remove();
      tooltip = null;
    }
  }
  
  // Start animation
  setTimeout(animatePolygon, 500);
}

// Generate circular progress chart
function generateCircularProgress(container, value, maxValue, label) {
  if (!container) return;
  
  // Calculate percentage
  const percent = Math.min(100, Math.max(0, (value / maxValue) * 100));
  
  // Create SVG element
  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("width", "100%");
  svg.setAttribute("height", "100%");
  svg.setAttribute("viewBox", "0 0 120 120");
  svg.style.transform = "rotate(-90deg)";
  container.appendChild(svg);
  
  // Center and radius
  const centerX = 60;
  const centerY = 60;
  const radius = 50;
  
  // Circle circumference
  const circumference = 2 * Math.PI * radius;
  
  // Background circle
  const bgCircle = document.createElementNS(svgNS, "circle");
  bgCircle.setAttribute("cx", centerX);
  bgCircle.setAttribute("cy", centerY);
  bgCircle.setAttribute("r", radius);
  bgCircle.setAttribute("fill", "transparent");
  bgCircle.setAttribute("stroke", "rgba(255, 255, 255, 0.1)");
  bgCircle.setAttribute("stroke-width", "8");
  svg.appendChild(bgCircle);
  
  // Progress circle
  const progressCircle = document.createElementNS(svgNS, "circle");
  progressCircle.setAttribute("cx", centerX);
  progressCircle.setAttribute("cy", centerY);
  progressCircle.setAttribute("r", radius);
  progressCircle.setAttribute("fill", "transparent");
  progressCircle.setAttribute("stroke", "var(--color-cyan)");
  progressCircle.setAttribute("stroke-width", "8");
  progressCircle.setAttribute("stroke-linecap", "round");
  progressCircle.setAttribute("stroke-dasharray", circumference);
  progressCircle.setAttribute("stroke-dashoffset", circumference);
  svg.appendChild(progressCircle);
  
  // Create value display
  const valueDisplay = document.createElement('div');
  valueDisplay.className = 'progress-value';
  valueDisplay.style.position = 'absolute';
  valueDisplay.style.top = '50%';
  valueDisplay.style.left = '50%';
  valueDisplay.style.transform = 'translate(-50%, -50%)';
  valueDisplay.style.fontSize = '1.5rem';
  valueDisplay.style.fontFamily = 'var(--font-heading)';
  valueDisplay.style.color = 'var(--color-cyan)';
  valueDisplay.textContent = '0%';
  container.appendChild(valueDisplay);
  
  // Create label if provided
  if (label) {
    const labelElement = document.createElement('div');
    labelElement.className = 'progress-label';
    labelElement.style.position = 'absolute';
    labelElement.style.top = 'calc(50% + 25px)';
    labelElement.style.left = '50%';
    labelElement.style.transform = 'translate(-50%, 0)';
    labelElement.style.fontSize = '0.8rem';
    labelElement.style.fontFamily = 'var(--font-body)';
    labelElement.style.color = 'var(--color-text-secondary)';
    labelElement.textContent = label;
    container.appendChild(labelElement);
  }
  
  // Animate progress
  setTimeout(() => {
    // Animate value display
    let displayValue = 0;
    const duration = 1500;
    const frameRate = 60;
    const increment = percent / (duration / (1000 / frameRate));
    const interval = 1000 / frameRate;
    
    const animation = setInterval(() => {
      displayValue += increment;
      
      if (displayValue >= percent) {
        displayValue = percent;
        clearInterval(animation);
      }
      
      // Update value display
      valueDisplay.textContent = `${Math.round(displayValue)}%`;
      
      // Update circle
      const offset = circumference - (displayValue / 100) * circumference;
      progressCircle.setAttribute("stroke-dashoffset", offset);
    }, interval);
  }, 500);
}

// Generate horizontal bar chart
function generateBarChart(container, data, options = {}) {
  if (!container || !data || !data.length) return;
  
  // Default options
  const defaults = {
    barHeight: 30,
    barGap: 10,
    barColor: 'var(--color-cyan)',
    labelColor: 'var(--color-text-secondary)',
    valueColor: 'var(--color-text)',
    maxValue: null,
    showValues: true,
    valuePosition: 'end', // 'end' or 'bar'
    showLabels: true,
    animate: true,
    animationDelay: 100
  };
  
  // Merge options
  const settings = Object.assign({}, defaults, options);
  
  // Calculate maximum value if not provided
  if (!settings.maxValue) {
    settings.maxValue = Math.max(...data.map(item => item.value));
  }
  
  // Calculate chart dimensions
  const chartHeight = (settings.barHeight + settings.barGap) * data.length;
  
  // Create chart container
  const chartContainer = document.createElement('div');
  chartContainer.className = 'bar-chart-container';
  chartContainer.style.height = `${chartHeight}px`;
  chartContainer.style.position = 'relative';
  container.appendChild(chartContainer);
  
  // Create bars
  data.forEach((item, index) => {
    // Container for label and bar
    const barContainer = document.createElement('div');
    barContainer.className = 'bar-container';
    barContainer.style.position = 'absolute';
    barContainer.style.top = `${index * (settings.barHeight + settings.barGap)}px`;
    barContainer.style.left = '0';
    barContainer.style.right = '0';
    barContainer.style.height = `${settings.barHeight}px`;
    barContainer.style.display = 'flex';
    barContainer.style.alignItems = 'center';
    chartContainer.appendChild(barContainer);
    
    // Label
    if (settings.showLabels) {
      const labelWidth = 100;
      
      const label = document.createElement('div');
      label.className = 'bar-label';
      label.style.width = `${labelWidth}px`;
      label.style.paddingRight = '10px';
      label.style.color = settings.labelColor;
      label.style.fontSize = '0.8rem';
      label.style.fontFamily = 'var(--font-body)';
      label.style.textAlign = 'right';
      label.style.whiteSpace = 'nowrap';
      label.style.overflow = 'hidden';
      label.style.textOverflow = 'ellipsis';
      label.textContent = item.label;
      barContainer.appendChild(label);
    }
    
    // Bar wrapper
    const barWrapper = document.createElement('div');
    barWrapper.className = 'bar-wrapper';
    barWrapper.style.flex = '1';
    barWrapper.style.height = '100%';
    barWrapper.style.position = 'relative';
    barWrapper.style.overflow = 'hidden';
    barContainer.appendChild(barWrapper);
    
    // Background bar
    const bgBar = document.createElement('div');
    bgBar.className = 'bar-background';
    bgBar.style.position = 'absolute';
    bgBar.style.top = '0';
    bgBar.style.left = '0';
    bgBar.style.width = '100%';
    bgBar.style.height = '100%';
    bgBar.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
    bgBar.style.borderRadius = '3px';
    barWrapper.appendChild(bgBar);
    
    // Progress bar
    const bar = document.createElement('div');
    bar.className = 'bar';
    bar.style.position = 'absolute';
    bar.style.top = '0';
    bar.style.left = '0';
    bar.style.width = '0';
    bar.style.height = '100%';
    bar.style.background = `linear-gradient(90deg, var(--color-cyan), var(--color-purple))`;
    bar.style.borderRadius = '3px';
    bar.style.transition = 'width 1s ease';
    barWrapper.appendChild(bar);
    
    // Value display
    if (settings.showValues) {
      const value = document.createElement('div');
      value.className = 'bar-value';
      value.style.position = 'absolute';
      value.style.top = '50%';
      value.style.transform = 'translateY(-50%)';
      value.style.color = settings.valueColor;
      value.style.fontSize = '0.8rem';
      value.style.fontFamily = 'var(--font-body)';
      value.style.whiteSpace = 'nowrap';
      value.textContent = item.value;
      
      if (settings.valuePosition === 'end') {
        value.style.left = '10px';
        barWrapper.appendChild(value);
      } else {
        value.style.right = '10px';
        bar.appendChild(value);
      }
    }
    
    // Animate bar
    if (settings.animate) {
      setTimeout(() => {
        // Set bar width based on value
        const percent = (item.value / settings.maxValue) * 100;
        bar.style.width = `${percent}%`;
        
        // Update value position for 'bar' position
        if (settings.showValues && settings.valuePosition === 'bar') {
          const value = bar.querySelector('.bar-value');
          if (value) {
            if (percent < 15) {
              value.style.left = 'calc(100% + 10px)';
              value.style.color = settings.valueColor;
            } else {
              value.style.left = '';
              value.style.right = '10px';
              value.style.color = '#fff';
            }
          }
        }
      }, settings.animationDelay * index);
    } else {
      // Set bar width immediately
      const percent = (item.value / settings.maxValue) * 100;
      bar.style.width = `${percent}%`;
    }
  });
}

// Generate data waveform visualization
function generateWaveform(container, data, options = {}) {
  if (!container || !data || !data.length) return;
  
  // Default options
  const defaults = {
    height: 100,
    barWidth: 3,
    barGap: 1,
    barColor: 'var(--color-cyan)',
    backgroundColor: 'rgba(10, 10, 26, 0.7)',
    animate: true,
    grid: true,
    responsive: true
  };
  
  // Merge options
  const settings = Object.assign({}, defaults, options);
  
  // Create waveform container
  const waveformContainer = document.createElement('div');
  waveformContainer.className = 'waveform-visualization';
  waveformContainer.style.position = 'relative';
  waveformContainer.style.height = `${settings.height}px`;
  waveformContainer.style.backgroundColor = settings.backgroundColor;
  waveformContainer.style.borderRadius = 'var(--border-radius-sm)';
  waveformContainer.style.overflow = 'hidden';
  container.appendChild(waveformContainer);
  
  // Add grid if enabled
  if (settings.grid) {
    const grid = document.createElement('div');
    grid.className = 'waveform-grid';
    grid.style.position = 'absolute';
    grid.style.top = '0';
    grid.style.left = '0';
    grid.style.right = '0';
    grid.style.bottom = '0';
    grid.style.backgroundImage = `
      linear-gradient(rgba(0, 240, 255, 0.1) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0, 240, 255, 0.1) 1px, transparent 1px)
    `;
    grid.style.backgroundSize = '20px 20px';
    grid.style.zIndex = '0';
    waveformContainer.appendChild(grid);
  }
  
  // Create waveform line
  const waveform = document.createElement('div');
  waveform.className = 'waveform-line';
  waveform.style.position = 'relative';
  waveform.style.height = '100%';
  waveform.style.display = 'flex';
  waveform.style.alignItems = 'center';
  waveform.style.justifyContent = 'center';
  waveform.style.zIndex = '1';
  waveformContainer.appendChild(waveform);
  
  // Normalize data to fit in container height
  const maxValue = Math.max(...data);
  const normalizedData = data.map(value => (value / maxValue) * (settings.height * 0.8));
  
  // Create bars
  normalizedData.forEach((height, index) => {
    const bar = document.createElement('div');
    bar.className = 'waveform-bar';
    bar.style.width = `${settings.barWidth}px`;
    bar.style.height = '0';
    bar.style.marginRight = `${settings.barGap}px`;
    bar.style.backgroundColor = settings.barColor;
    bar.style.borderRadius = '1px';
    bar.style.transition = settings.animate ? 'height 0.2s ease' : 'none';
    waveform.appendChild(bar);
    
    // Animate bar height
    if (settings.animate) {
      setTimeout(() => {
        bar.style.height = `${height}px`;
      }, index * 10);
    } else {
      bar.style.height = `${height}px`;
    }
  });
  
  // Add scanning effect
  const scanLine = document.createElement('div');
  scanLine.className = 'scan-line';
  scanLine.style.position = 'absolute';
  scanLine.style.top = '0';
  scanLine.style.left = '0';
  scanLine.style.width = '100%';
  scanLine.style.height = '1px';
  scanLine.style.backgroundColor = 'rgba(0, 240, 255, 0.5)';
  scanLine.style.boxShadow = '0 0 10px rgba(0, 240, 255, 0.7)';
  scanLine.style.zIndex = '2';
  waveformContainer.appendChild(scanLine);
  
  // Animate scan line
  function animateScanLine() {
    scanLine.style.top = '0';
    
    // Force reflow
    scanLine.offsetHeight;
    
    // Set transition
    scanLine.style.transition = 'top 2s linear';
    scanLine.style.top = `${settings.height}px`;
    
    // Reset after animation completes
    setTimeout(() => {
      scanLine.style.transition = 'none';
      // Slight delay before starting again
      setTimeout(animateScanLine, 500);
    }, 2000);
  }
  
  // Start scan animation
  setTimeout(animateScanLine, 1000);
  
  // Handle responsive resizing if enabled
  if (settings.responsive) {
    window.addEventListener('resize', debounce(() => {
      // Get container width
      const containerWidth = waveformContainer.offsetWidth;
      
      // Calculate how many bars can fit
      const barsPerContainer = Math.floor(containerWidth / (settings.barWidth + settings.barGap));
      
      // Resize data if needed
      if (barsPerContainer < data.length) {
        // Remove excess bars
        while (waveform.children.length > barsPerContainer) {
          waveform.removeChild(waveform.lastChild);
        }
      } else if (barsPerContainer > waveform.children.length && waveform.children.length < data.length) {
        // Add more bars up to original data length
        const startIndex = waveform.children.length;
        for (let i = startIndex; i < Math.min(barsPerContainer, data.length); i++) {
          const height = normalizedData[i];
          const bar = document.createElement('div');
          bar.className = 'waveform-bar';
          bar.style.width = `${settings.barWidth}px`;
          bar.style.height = `${height}px`;
          bar.style.marginRight = `${settings.barGap}px`;
          bar.style.backgroundColor = settings.barColor;
          bar.style.borderRadius = '1px';
          waveform.appendChild(bar);
        }
      }
    }, 250));
  }
}