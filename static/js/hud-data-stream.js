/**
 * HUD Data Stream Visualization
 * Creates a futuristic terminal-style data stream visualization
 * Perfect for adding to blog (datalog) headers or as background elements
 */

class HUDDataStream {
    constructor(container, options = {}) {
      // Default options
      this.options = {
        columns: 10,                     // Number of data columns
        rows: 4,                         // Number of data rows
        updateSpeed: 100,                // Update interval in ms
        fontFamily: 'JetBrains Mono',    // Font family
        fontSize: '12px',                // Font size
        streamColors: ['#00f0ff', '#7928ca'], // Primary colors for data
        backgroundColor: 'rgba(10, 10, 26, 0.7)', // Background color
        showTimestamp: true,             // Show timestamp
        showHeaders: true,               // Show column headers
        animate: true,                   // Animate updates
        theme: 'cyber',                  // Theme: 'cyber', 'matrix', 'terminal'
        dataType: 'metrics',             // Type of data to display: 'metrics', 'logs', 'code'
        ...options
      };
      
      this.container = typeof container === 'string' ? document.querySelector(container) : container;
      this.running = false;
      this.data = [];
      this.headers = [];
      this.updateTimer = null;
      
      if (this.container) {
        this.init();
      } else {
        console.error('HUD Data Stream: Container not found');
      }
    }
    
    init() {
      // Set container styles
      this.container.style.fontFamily = this.options.fontFamily;
      this.container.style.fontSize = this.options.fontSize;
      this.container.style.backgroundColor = this.options.backgroundColor;
      this.container.style.borderRadius = '4px';
      this.container.style.padding = '15px';
      this.container.style.color = this.options.streamColors[0];
      this.container.style.overflow = 'hidden';
      this.container.style.position = 'relative';
      this.container.style.minHeight = '150px';
      
      // Create HUD frame
      this.createHUDFrame();
      
      // Generate initial data
      this.generateData();
      
      // Create main elements
      this.createElements();
      
      // Start animation if enabled
      if (this.options.animate) {
        this.start();
      } else {
        this.render();
      }
    }
    
    createHUDFrame() {
      // Add corner elements to create HUD frame
      const corners = ['tl', 'tr', 'bl', 'br'];
      
      corners.forEach(corner => {
        const el = document.createElement('div');
        el.className = `hud-corner hud-corner-${corner}`;
        el.style.position = 'absolute';
        el.style.width = '15px';
        el.style.height = '15px';
        el.style.borderColor = this.options.streamColors[0];
        el.style.borderStyle = 'solid';
        el.style.zIndex = '1';
        
        // Position and style based on corner
        switch(corner) {
          case 'tl':
            el.style.top = '5px';
            el.style.left = '5px';
            el.style.borderWidth = '2px 0 0 2px';
            break;
          case 'tr':
            el.style.top = '5px';
            el.style.right = '5px';
            el.style.borderWidth = '2px 2px 0 0';
            break;
          case 'bl':
            el.style.bottom = '5px';
            el.style.left = '5px';
            el.style.borderWidth = '0 0 2px 2px';
            break;
          case 'br':
            el.style.bottom = '5px';
            el.style.right = '5px';
            el.style.borderWidth = '0 2px 2px 0';
            break;
        }
        
        this.container.appendChild(el);
      });
      
      // Add scan line effect
      const scanLine = document.createElement('div');
      scanLine.className = 'hud-scan-line';
      scanLine.style.position = 'absolute';
      scanLine.style.top = '0';
      scanLine.style.left = '0';
      scanLine.style.right = '0';
      scanLine.style.height = '2px';
      scanLine.style.background = `linear-gradient(to right, transparent, ${this.options.streamColors[0]}, transparent)`;
      scanLine.style.opacity = '0.6';
      scanLine.style.zIndex = '2';
      scanLine.style.animation = 'hud-scan 3s linear infinite';
      
      // Add keyframes for scan animation
      if (!document.getElementById('hud-stream-keyframes')) {
        const style = document.createElement('style');
        style.id = 'hud-stream-keyframes';
        style.textContent = `
          @keyframes hud-scan {
            0% { transform: translateY(0); opacity: 0; }
            10% { opacity: 0.6; }
            90% { opacity: 0.6; }
            100% { transform: translateY(100%); opacity: 0; }
          }
          
          @keyframes hud-blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
          }
          
          @keyframes hud-pulse {
            0%, 100% { text-shadow: 0 0 2px ${this.options.streamColors[0]}; }
            50% { text-shadow: 0 0 8px ${this.options.streamColors[0]}; }
          }
        `;
        document.head.appendChild(style);
      }
      
      this.container.appendChild(scanLine);
    }
    
    createElements() {
      // Create wrapper element
      this.wrapper = document.createElement('div');
      this.wrapper.className = 'hud-data-stream-wrapper';
      this.wrapper.style.position = 'relative';
      this.wrapper.style.zIndex = '3';
      this.wrapper.style.margin = '10px';
      
      // Create header (timestamp + status)
      if (this.options.showTimestamp) {
        this.header = document.createElement('div');
        this.header.className = 'hud-data-stream-header';
        this.header.style.display = 'flex';
        this.header.style.justifyContent = 'space-between';
        this.header.style.marginBottom = '10px';
        this.header.style.padding = '5px';
        this.header.style.borderBottom = `1px solid ${this.options.streamColors[0]}`;
        this.header.style.fontFamily = this.options.fontFamily;
        this.header.style.fontSize = '0.9em';
        this.header.style.opacity = '0.8';
        
        // Timestamp element
        this.timestamp = document.createElement('div');
        this.timestamp.className = 'hud-data-stream-timestamp';
        this.updateTimestamp();
        
        // Status element
        this.status = document.createElement('div');
        this.status.className = 'hud-data-stream-status';
        this.status.innerHTML = 'STATUS: <span style="color:' + this.options.streamColors[0] + '">ONLINE</span>';
        this.status.querySelector('span').style.animation = 'hud-blink 2s infinite';
        
        this.header.appendChild(this.timestamp);
        this.header.appendChild(this.status);
        this.wrapper.appendChild(this.header);
      }
      
      // Create table for data
      this.table = document.createElement('div');
      this.table.className = 'hud-data-stream-table';
      
      // Add table headers if enabled
      if (this.options.showHeaders) {
        const headerRow = document.createElement('div');
        headerRow.className = 'hud-data-stream-row hud-headers';
        headerRow.style.display = 'flex';
        headerRow.style.fontWeight = 'bold';
        headerRow.style.marginBottom = '5px';
        headerRow.style.color = this.options.streamColors[0];
        
        this.headers.forEach(header => {
          const cell = document.createElement('div');
          cell.className = 'hud-data-stream-cell';
          cell.textContent = header;
          cell.style.flex = '1';
          cell.style.padding = '5px';
          cell.style.animation = 'hud-pulse 3s infinite';
          headerRow.appendChild(cell);
        });
        
        this.table.appendChild(headerRow);
      }
      
      // Add data rows
      for (let i = 0; i < this.options.rows; i++) {
        const row = document.createElement('div');
        row.className = 'hud-data-stream-row';
        row.style.display = 'flex';
        row.style.marginBottom = '5px';
        row.style.padding = '3px 0';
        row.style.borderBottom = '1px solid rgba(0, 240, 255, 0.1)';
        
        // Add columns for this row
        for (let j = 0; j < this.options.columns; j++) {
          const cell = document.createElement('div');
          cell.className = 'hud-data-stream-cell';
          cell.style.flex = '1';
          cell.style.padding = '5px';
          cell.style.opacity = '0.9';
          cell.style.transition = 'all 0.3s ease';
          
          row.appendChild(cell);
        }
        
        this.table.appendChild(row);
      }
      
      this.wrapper.appendChild(this.table);
      this.container.appendChild(this.wrapper);
    }
    
    generateData() {
      // Generate random headers and data based on dataType
      this.headers = [];
      this.data = [];
      
      switch(this.options.dataType) {
        case 'metrics':
          this.headers = ['SYSTEM', 'CPU', 'MEMORY', 'NETWORK', 'STATUS', 'LOAD', 'UPTIME', 'TASKS', 'ERRORS', 'THROUGHPUT'];
          
          // Generate rows of metric data
          for (let i = 0; i < this.options.rows; i++) {
            const row = [
              `SYS-${String.fromCharCode(65 + Math.floor(Math.random() * 26))}${Math.floor(Math.random() * 100)}`,
              `${(Math.random() * 100).toFixed(1)}%`,
              `${(Math.random() * 32).toFixed(1)} GB`,
              `${Math.floor(Math.random() * 1000)} MB/s`,
              Math.random() > 0.8 ? 'WARNING' : 'NOMINAL',
              `${(Math.random() * 10).toFixed(2)}`,
              `${Math.floor(Math.random() * 24)}h${Math.floor(Math.random() * 60)}m`,
              `${Math.floor(Math.random() * 100)}`,
              `${Math.floor(Math.random() * 10)}`,
              `${Math.floor(Math.random() * 1000)} req/s`
            ];
            
            // Trim array to match column count
            this.data.push(row.slice(0, this.options.columns));
          }
          break;
          
        case 'logs':
          this.headers = ['TIMESTAMP', 'LEVEL', 'SERVICE', 'MESSAGE', 'TRACE', 'USER', 'IP', 'ACTION', 'DURATION', 'CODE'];
          
          // Log levels with colors
          const levels = [
            {text: 'INFO', color: '#5edfff'},
            {text: 'DEBUG', color: '#28a332'},
            {text: 'WARN', color: '#ffbd2e'},
            {text: 'ERROR', color: '#ff6b8b'},
            {text: 'CRITICAL', color: '#ff0000'}
          ];
          
          // Generate rows of log data
          for (let i = 0; i < this.options.rows; i++) {
            const level = levels[Math.floor(Math.random() * levels.length)];
            const timestamp = new Date(Date.now() - Math.floor(Math.random() * 3600000));
            
            const row = [
              `${timestamp.toISOString().split('T')[1].split('.')[0]}`,
              `<span style="color:${level.color}">${level.text}</span>`,
              `${['API', 'DB', 'AUTH', 'CACHE', 'WORKER'][Math.floor(Math.random() * 5)]}`,
              `${['Request processed', 'Data fetched', 'Connection established', 'Operation completed', 'Task scheduled'][Math.floor(Math.random() * 5)]}`,
              `${Math.random().toString(36).substring(2, 10)}`,
              `user_${Math.floor(Math.random() * 100)}`,
              `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
              `${['GET', 'POST', 'PUT', 'DELETE'][Math.floor(Math.random() * 4)]}`,
              `${Math.floor(Math.random() * 1000)}ms`,
              `${Math.floor(Math.random() * 500)}`
            ];
            
            // Trim array to match column count
            this.data.push(row.slice(0, this.options.columns));
          }
          break;
          
        case 'code':
          this.headers = ['LINE', 'CODE', 'EXEC', 'RESULT', 'TIME', 'MEM', 'STACK', 'HEAP', 'DEPTH', 'REFS'];
          
          // Generate rows of code execution data
          const functions = ['init()', 'process()', 'compute()', 'analyze()', 'transform()', 'validate()', 'execute()'];
          
          for (let i = 0; i < this.options.rows; i++) {
            const row = [
              `${Math.floor(Math.random() * 1000)}`,
              `<span style="color:#7928ca">${functions[Math.floor(Math.random() * functions.length)]}</span>`,
              `${Math.random() > 0.9 ? 'PENDING' : 'COMPLETE'}`,
              `${Math.random() > 0.8 ? 'ERR' : 'OK'}-${Math.floor(Math.random() * 100)}`,
              `${Math.floor(Math.random() * 100)}ms`,
              `${Math.floor(Math.random() * 100)}MB`,
              `${Math.floor(Math.random() * 10)}`,
              `${Math.floor(Math.random() * 1000)}MB`,
              `${Math.floor(Math.random() * 5)}`,
              `${Math.floor(Math.random() * 50)}`
            ];
            
            // Trim array to match column count
            this.data.push(row.slice(0, this.options.columns));
          }
          break;
      }
      
      // Trim headers to match column count
      this.headers = this.headers.slice(0, this.options.columns);
    }
    
    updateTimestamp() {
      if (this.timestamp) {
        const now = new Date();
        const timeStr = now.toISOString().split('T')[1].split('.')[0];
        this.timestamp.textContent = `TIME: ${timeStr}`;
      }
    }
    
    render() {
      // Update the timestamp
      this.updateTimestamp();
      
      // Update the data cells
      const rows = this.table.querySelectorAll('.hud-data-stream-row:not(.hud-headers)');
      
      rows.forEach((row, rowIndex) => {
        if (rowIndex < this.data.length) {
          const cells = row.querySelectorAll('.hud-data-stream-cell');
          
          cells.forEach((cell, cellIndex) => {
            if (cellIndex < this.data[rowIndex].length) {
              cell.innerHTML = this.data[rowIndex][cellIndex];
              
              // Add special styling for specific values
              if (this.options.dataType === 'metrics') {
                // Highlight warnings
                if (this.data[rowIndex][cellIndex] === 'WARNING') {
                  cell.style.color = '#ffbd2e';
                } else if (this.data[rowIndex][cellIndex] === 'ERROR') {
                  cell.style.color = '#ff6b8b';
                } else {
                  cell.style.color = '';
                }
                
                // Highlight high CPU/memory usage
                if (cellIndex === 1 || cellIndex === 2) {
                  const valueStr = this.data[rowIndex][cellIndex];
                  const value = parseFloat(valueStr);
                  
                  if (value > 90) {
                    cell.style.color = '#ff6b8b';
                  } else if (value > 70) {
                    cell.style.color = '#ffbd2e';
                  } else {
                    cell.style.color = '#28a332';
                  }
                }
              }
            }
          });
        }
      });
    }
    
    update() {
      // Generate new random data
      this.generateData();
      
      // Render the updated data
      this.render();
    }
    
    start() {
      if (!this.running) {
        this.running = true;
        this.render();
        
        // Set up timer for updates
        this.updateTimer = setInterval(() => {
          this.update();
        }, this.options.updateSpeed);
      }
    }
    
    stop() {
      if (this.running) {
        this.running = false;
        clearInterval(this.updateTimer);
        this.updateTimer = null;
      }
    }
    
    destroy() {
      this.stop();
      this.container.innerHTML = '';
    }
  }
  
  // Example usage:
  // const dataStream = new HUDDataStream('#data-stream-container', {
  //   columns: 6,
  //   rows: 5,
  //   dataType: 'metrics', // 'metrics', 'logs', or 'code'
  //   updateSpeed: 2000 // Update every 2 seconds
  // });