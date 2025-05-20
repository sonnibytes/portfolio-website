/**
 * Enhanced Tech Interface JavaScript
 * Adds dynamic elements and animations to the futuristic tech interface
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize UI components
    initializeCircularProgress();
    initializeProgressBars();
    initializeSkillBars();
    initializeWaveforms();
    initializePulseDots();
    createScanLine();
    initializeAnimatedElements();
    
    // Add hexagonal category indicators if they exist
    if (document.querySelector('.category-container')) {
      initializeCategoryHexagons();
    }
    
    // Add terminal functionality if it exists
    if (document.querySelector('.terminal-container')) {
      initializeTerminal();
    }
  });
  
  /**
   * Initialize circular progress indicators
   */
  function initializeCircularProgress() {
    const circularProgressElements = document.querySelectorAll('.circular-progress');
    
    circularProgressElements.forEach(progress => {
      const progressValue = progress.getAttribute('data-progress') || 0;
      const size = progress.offsetWidth;
      const strokeWidth = 3;
      const radius = (size / 2) - (strokeWidth * 2);
      const circumference = radius * 2 * Math.PI;
      
      // Create SVG element
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('width', size);
      svg.setAttribute('height', size);
      
      // Create background circle
      const circleBackground = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circleBackground.setAttribute('class', 'circular-progress-bg');
      circleBackground.setAttribute('cx', size / 2);
      circleBackground.setAttribute('cy', size / 2);
      circleBackground.setAttribute('r', radius);
      circleBackground.setAttribute('stroke-width', strokeWidth);
      
      // Create progress circle
      const circleProgress = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circleProgress.setAttribute('class', 'circular-progress-ring');
      circleProgress.setAttribute('cx', size / 2);
      circleProgress.setAttribute('cy', size / 2);
      circleProgress.setAttribute('r', radius);
      circleProgress.setAttribute('stroke-width', strokeWidth);
      circleProgress.setAttribute('stroke-dasharray', circumference);
      
      // Add circles to SVG
      svg.appendChild(circleBackground);
      svg.appendChild(circleProgress);
      
      // Add SVG to container (before any inner content)
      progress.insertBefore(svg, progress.firstChild);
      
      // Add inner content if not present
      if (!progress.querySelector('.circular-progress-inner')) {
        const inner = document.createElement('div');
        inner.classList.add('circular-progress-inner');
        
        const value = document.createElement('div');
        value.classList.add('circular-progress-value');
        value.textContent = progressValue + '%';
        
        const label = document.createElement('div');
        label.classList.add('circular-progress-label');
        label.textContent = 'COMPLETE';
        
        inner.appendChild(value);
        inner.appendChild(label);
        progress.appendChild(inner);
      }
      
      // Animate progress
      setTimeout(() => {
        const offset = circumference - (progressValue / 100 * circumference);
        circleProgress.style.strokeDashoffset = offset;
      }, 100);
    });
  }
  
  /**
   * Initialize progress bars with animation
   */
  function initializeProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar-fill');
    
    progressBars.forEach(bar => {
      const width = bar.getAttribute('data-width');
      
      // Start with 0 width
      bar.style.width = '0%';
      
      // Animate to target width
      setTimeout(() => {
        bar.style.width = width + '%';
      }, 300);
    });
  }
  
  /**
   * Initialize skill bars with animation
   */
  function initializeSkillBars() {
    const skillBars = document.querySelectorAll('.skill-level');
    
    skillBars.forEach(bar => {
      const percentage = bar.getAttribute('data-percentage') || bar.style.height;
      
      // Add markers if not present
      if (!bar.querySelector('.skill-marker')) {
        const marker = document.createElement('div');
        marker.classList.add('skill-marker');
        bar.appendChild(marker);
      }
      
      // Start with 0 height
      bar.style.height = '0%';
      
      // Animate to target height
      setTimeout(() => {
        bar.style.height = percentage;
        
        // Position the marker
        const marker = bar.querySelector('.skill-marker');
        if (marker) {
          marker.style.bottom = percentage;
        }
      }, 300);
    });
  }
  
  /**
   * Initialize waveforms with dynamic creation
   */
  function initializeWaveforms() {
    const waveforms = document.querySelectorAll('.waveform');
    
    waveforms.forEach(waveform => {
      // Clear existing content
      waveform.innerHTML = '';
      
      // Create center line
      const centerLine = document.createElement('div');
      centerLine.classList.add('waveform-line');
      waveform.appendChild(centerLine);
      
      // Create bars container
      const barsContainer = document.createElement('div');
      barsContainer.classList.add('waveform-bars');
      
      // Create dynamic bars
      const barCount = Math.floor(waveform.offsetWidth / 5);
      
      for (let i = 0; i < barCount; i++) {
        const bar = document.createElement('div');
        bar.classList.add('waveform-bar');
        
        // Random height values for the animation
        const minHeight = Math.floor(Math.random() * 8) + 4; // 4-12px
        const maxHeight = Math.floor(Math.random() * 20) + 15; // 15-35px
        
        bar.style.setProperty('--index', i);
        bar.style.setProperty('--min-height', `${minHeight}px`);
        bar.style.setProperty('--max-height', `${maxHeight}px`);
        bar.style.setProperty('--height', `${minHeight}px`);
        
        barsContainer.appendChild(bar);
      }
      
      waveform.appendChild(barsContainer);
    });
  }
  
  /**
   * Creates random pulse dots on the interface
   */
  function initializePulseDots() {
    // Remove any existing pulse dots
    document.querySelectorAll('.pulse').forEach(dot => dot.remove());
    
    // Create new pulse dots
    for (let i = 0; i < 3; i++) {
      createPulseDot();
    }
  }
  
  /**
   * Creates a single pulse dot
   */
  function createPulseDot() {
    const pulse = document.createElement('div');
    pulse.classList.add('pulse');
    
    // Random position
    pulse.style.top = Math.random() * 100 + '%';
    pulse.style.left = Math.random() * 100 + '%';
    
    document.body.appendChild(pulse);
    
    // Remove and recreate the pulse dot after animation
    setTimeout(() => {
      pulse.remove();
      createPulseDot();
    }, 4000);
  }
  
  /**
   * Create a scan line effect
   */
  function createScanLine() {
    const scanLine = document.createElement('div');
    scanLine.classList.add('scan-line');
    document.body.appendChild(scanLine);
  }
  
  /**
   * Initialize animated entrance for UI elements
   */
  function initializeAnimatedElements() {
    // Apply staggered fade-in effects
    const elements = document.querySelectorAll('.tech-container, .system-card, .datalog-entry');
    
    elements.forEach((element, index) => {
      element.classList.add('fade-in');
      element.style.animationDelay = `${index * 0.1}s`;
    });
  }
  
  /**
   * Initialize hexagonal category indicators
   */
  function initializeCategoryHexagons() {
    const categories = document.querySelectorAll('.category-item');
    
    categories.forEach(category => {
      if (!category.querySelector('.category-hexagon')) {
        const code = category.getAttribute('data-code') || '';
        const name = category.getAttribute('data-name') || '';
        
        const hexagon = document.createElement('div');
        hexagon.classList.add('category-hexagon');
        
        const inner = document.createElement('div');
        inner.classList.add('category-hexagon-inner');
        
        const codeElement = document.createElement('div');
        codeElement.classList.add('category-code');
        codeElement.textContent = code;
        
        const labelElement = document.createElement('div');
        labelElement.classList.add('category-label');
        labelElement.textContent = name;
        
        inner.appendChild(codeElement);
        inner.appendChild(labelElement);
        hexagon.appendChild(inner);
        
        category.appendChild(hexagon);
      }
    });
  }
  
  /**
   * Initialize terminal with basic command functionality
   */
  function initializeTerminal() {
    const terminal = document.querySelector('.terminal-container');
    const input = document.querySelector('.terminal-input');
    
    if (!terminal || !input) return;
    
    // Add initial greeting
    addTerminalLine('SYSTEM', 'Terminal initialized. Type "help" for available commands.', 'terminal-response');
    
    // Handle command input
    input.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        
        const command = input.value.trim().toLowerCase();
        
        // Add command to terminal
        addTerminalLine('USER', command, 'terminal-command');
        
        // Process command
        processCommand(command);
        
        // Clear input
        input.value = '';
      }
    });
    
    /**
     * Process terminal commands
     */
    function processCommand(command) {
      switch(command) {
        case 'help':
          addTerminalLine('SYSTEM', 'Available commands:', 'terminal-response');
          addTerminalLine('SYSTEM', '- help: Display this help message', 'terminal-response');
          addTerminalLine('SYSTEM', '- about: Information about the developer', 'terminal-response');
          addTerminalLine('SYSTEM', '- skills: List developer skills', 'terminal-response');
          addTerminalLine('SYSTEM', '- projects: List projects/systems', 'terminal-response');
          addTerminalLine('SYSTEM', '- contact: Show contact information', 'terminal-response');
          addTerminalLine('SYSTEM', '- clear: Clear terminal', 'terminal-response');
          break;
          
        case 'about':
          addTerminalLine('SYSTEM', 'Developer Profile:', 'terminal-response');
          addTerminalLine('SYSTEM', 'Python developer specializing in Django web applications, data analysis, and machine learning integration.', 'terminal-response');
          break;
          
        case 'skills':
          addTerminalLine('SYSTEM', 'Technical Skills:', 'terminal-response');
          addTerminalLine('SYSTEM', '- Python/Django: Advanced', 'terminal-response');
          addTerminalLine('SYSTEM', '- JavaScript: Intermediate', 'terminal-response');
          addTerminalLine('SYSTEM', '- Data Analysis: Advanced', 'terminal-response');
          addTerminalLine('SYSTEM', '- Machine Learning: Intermediate', 'terminal-response');
          break;
          
        case 'projects':
          addTerminalLine('SYSTEM', 'Systems Overview:', 'terminal-response');
          addTerminalLine('SYSTEM', '- AI-Powered Data Analysis Platform', 'terminal-response');
          addTerminalLine('SYSTEM', '- Django Portfolio with Futuristic UI', 'terminal-response');
          addTerminalLine('SYSTEM', '- Custom CMS with ML Content Suggestions', 'terminal-response');
          break;
          
        case 'contact':
          addTerminalLine('SYSTEM', 'Contact Information:', 'terminal-response');
          addTerminalLine('SYSTEM', '- GitHub: @yourusername', 'terminal-response');
          addTerminalLine('SYSTEM', '- Email: you@example.com', 'terminal-response');
          addTerminalLine('SYSTEM', '- LinkedIn: Your Name', 'terminal-response');
          break;
          
        case 'clear':
          terminal.innerHTML = '';
          addTerminalLine('SYSTEM', 'Terminal cleared.', 'terminal-response');
          break;
          
        default:
          addTerminalLine('SYSTEM', `Command not recognized: "${command}". Type "help" for available commands.`, 'terminal-error');
      }
    }
    
    /**
     * Add a line to the terminal
     */
    function addTerminalLine(prefix, text, className) {
      const line = document.createElement('div');
      line.classList.add('terminal-line');
      
      const promptElement = document.createElement('span');
      promptElement.classList.add('terminal-prompt');
      promptElement.textContent = `[${prefix}]>`;
      
      const contentElement = document.createElement('span');
      contentElement.classList.add(className);
      contentElement.textContent = text;
      
      line.appendChild(promptElement);
      line.appendChild(contentElement);
      
      terminal.appendChild(line);
      
      // Scroll to bottom
      terminal.scrollTop = terminal.scrollHeight;
    }
  }
  
  /**
   * Add a hexagon component dynamically
   * @param {string} containerSelector - The CSS selector for the container
   * @param {string} text - The text to display in the hexagon
   */
  function addHexagon(containerSelector, text) {
    const container = document.querySelector(containerSelector);
    if (!container) return;
    
    const hexagon = document.createElement('div');
    hexagon.classList.add('hexagon');
    hexagon.textContent = text;
    
    container.appendChild(hexagon);
  }
  
  /**
   * Create a circular visualization with data points
   * @param {string} containerSelector - The CSS selector for the container
   * @param {Array} dataPoints - Array of {label, value, angle} objects
   */
  function createRadialVisualization(containerSelector, dataPoints) {
    const container = document.querySelector(containerSelector);
    if (!container) return;
    
    container.classList.add('radial-menu');
    
    // Create center
    const center = document.createElement('div');
    center.classList.add('radial-menu-center');
    center.innerHTML = '<i class="fas fa-broadcast-tower"></i>';
    
    // Create ring
    const ring = document.createElement('div');
    ring.classList.add('radial-menu-ring');
    
    container.appendChild(ring);
    
    // Add data points
    dataPoints.forEach(point => {
      const angle = point.angle * (Math.PI / 180);
      const radius = container.offsetWidth / 2 * 0.8;
      
      const x = Math.cos(angle) * radius + radius;
      const y = Math.sin(angle) * radius + radius;
      
      const item = document.createElement('div');
      item.classList.add('radial-menu-item');
      item.style.left = `${x}px`;
      item.style.top = `${y}px`;
      item.setAttribute('title', `${point.label}: ${point.value}`);
      
      container.appendChild(item);
    });
    
    container.appendChild(center);
  }
  
  /**
   * Create a line graph visualization
   * @param {string} containerSelector - The CSS selector for the container
   * @param {Array} dataPoints - Array of {x, y, label} objects
   */
  function createLineVisualization(containerSelector, dataPoints) {
    const container = document.querySelector(containerSelector);
    if (!container) return;
    
    // Clear container
    container.innerHTML = '';
    
    // Add visualization container
    const vizContainer = document.createElement('div');
    vizContainer.classList.add('visualization-container');
    
    // Add grid
    const grid = document.createElement('div');
    grid.classList.add('visualization-grid');
    
    // Add line
    const line = document.createElement('div');
    line.classList.add('visualization-line');
    
    vizContainer.appendChild(grid);
    vizContainer.appendChild(line);
    
    // Add data points
    const maxX = Math.max(...dataPoints.map(p => p.x));
    const maxY = Math.max(...dataPoints.map(p => p.y));
    
    dataPoints.forEach(point => {
      const x = (point.x / maxX * 100);
      const y = 100 - (point.y / maxY * 100);
      
      const dataPoint = document.createElement('div');
      dataPoint.classList.add('data-point');
      dataPoint.style.left = `${x}%`;
      dataPoint.style.top = `${y}%`;
      dataPoint.setAttribute('title', `${point.label}: ${point.y}`);
      
      vizContainer.appendChild(dataPoint);
    });
    
    container.appendChild(vizContainer);
  }