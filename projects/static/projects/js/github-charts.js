// projects/static/projects/js/github-charts.js
// GitHub Charts Manager - Fixed JSON data handling

class GitHubChartsManager {
    constructor() {
        this.charts = new Map();
        this.colors = {
            primary: '#7c3aed',
            success: '#10b981', 
            warning: '#f59e0b',
            info: '#3b82f6',
            background: 'rgba(124, 58, 237, 0.1)',
            grid: 'rgba(148, 163, 184, 0.2)',
            text: '#94a3b8'
        };
        
        this.init();
    }
    
    init() {
        // Check if Chart.js is available
        if (typeof Chart === 'undefined') {
            console.error('Chart.js not loaded - charts will not work');
            return;
        }
        
        console.log('Initializing GitHub Charts Manager...');
        
        // Initialize all charts on page
        this.initializeCharts();
        
        // Setup event listeners
        this.setupEventListeners();
    }
    
    initializeCharts() {
        const chartElements = document.querySelectorAll('.commit-chart');
        console.log(`Found ${chartElements.length} GitHub charts to initialize`);
        
        chartElements.forEach(canvas => {
            try {
                const chartId = canvas.id;
                
                // NEW: Get chart data from JSON script tag instead of canvas attribute
                const chartData = this.getChartDataFromScript(chartId);
                
                if (chartData && chartData.labels && chartData.labels.length > 0) {
                    this.createCommitChart(canvas, chartData, chartId);
                } else {
                    console.warn('No valid chart data for', chartId);
                    console.log('Chart data found:', chartData);
                }
            } catch (error) {
                console.error('Failed to initialize chart:', canvas.id, error);
            }
        });
    }
    
    getChartDataFromScript(chartId) {
        // Extract slug from chart ID (e.g., "weeklyCommitsChart-all-projects" -> "all-projects")
        const slug = chartId.replace('weeklyCommitsChart-', '');
        const scriptId = `chartData-${slug}`;
        
        try {
            const scriptElement = document.getElementById(scriptId);
            if (!scriptElement) {
                console.warn(`No chart data script found with ID: ${scriptId}`);
                return null;
            }
            
            const jsonText = scriptElement.textContent || scriptElement.innerText;
            console.log(`Found chart data script for ${slug}:`, jsonText.substring(0, 100) + '...');
            
            const chartData = JSON.parse(jsonText);
            console.log('Parsed chart data:', chartData);
            
            return chartData;
        } catch (error) {
            console.error(`Error parsing chart data for ${scriptId}:`, error);
            return null;
        }
    }
    
    createCommitChart(canvas, data, chartId) {
        const ctx = canvas.getContext('2d');
        
        // Chart.js v3 compatible configuration
        const config = {
            type: 'line',
            data: this.prepareChartData(data, 'weekly'),
            options: this.getChartOptions('weekly'),
            plugins: []
        };

        try {
        // Create chart
        const chart = new Chart(ctx, config);
        this.charts.set(chartId, chart);
        
            // Setup toggle functionality if toggle buttons exist
        this.setupChartToggle(chartId, data);
        
        console.log('✅ Created GitHub chart:', chartId);
            return chart;
        } catch (error) {
            console.error('Failed to create chart:', chartId, error);
            return null;
        }
    }
    
    prepareChartData(rawData, viewType = 'weekly') {
        const isWeekly = viewType === 'weekly';
        const labels = isWeekly ? rawData.labels : rawData.monthly_labels;
        const commits = isWeekly ? rawData.weekly : rawData.monthly;

        // Ensure arrays exist and have data
        const safeLabels = Array.isArray(labels) ? labels : [];
        const safeCommits = Array.isArray(commits) ? commits : [];

        console.log(`Preparing ${viewType} chart data:`, {
            labels: safeLabels.length,
            commits: safeCommits.length
        });

        return {
            labels: safeLabels,
            datasets: [{
                label: isWeekly ? 'Weekly Commits' : 'Monthly Commits',
                data: safeCommits,
                borderColor: this.colors.primary,
                backgroundColor: this.colors.background,
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: this.colors.primary,
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7,
                pointHoverBackgroundColor: this.colors.success,
                pointHoverBorderColor: '#ffffff',
                pointHoverBorderWidth: 3
            }]
        };
    }
    
    getChartOptions(viewType = 'weekly') {
        const isWeekly = viewType === 'weekly';
        
        return {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: { 
                    display: false 
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#f0f6fc',
                    bodyColor: '#94a3b8',
                    borderColor: this.colors.primary,
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 12,
                    callbacks: {
                        title: function(context) {
                            return context[0].label;
                        },
                        label: function(context) {
                            const count = context.parsed.y;
                            const period = isWeekly ? 'week' : 'month';
                            if (count === 0) {
                                return `No commits this ${period}`;
                            } else if (count === 1) {
                                return `1 commit this ${period}`;
                            } else {
                                return `${count} commits this ${period}`;
                            }
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: this.colors.grid,
                        borderColor: this.colors.grid
                    },
                    ticks: {
                        color: this.colors.text,
                        font: { 
                            size: 11 
                        },
                        maxRotation: 45
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: this.colors.grid,
                        borderColor: this.colors.grid
                    },
                    ticks: {
                        color: this.colors.text,
                        font: { 
                            size: 11 
                        },
                        stepSize: 1,
                        callback: function(value) {
                            // Only show integer values
                            if (Number.isInteger(value)) {
                                return value;
                            }
                        }
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeInOutQuart'
            }
        };
    }
    
    setupChartToggle(chartId, rawData) {
        const chartCanvas = document.getElementById(chartId);
        if (!chartCanvas) return;

        const chartContainer = chartCanvas.closest('.chart-container');
        if (!chartContainer) return;

        const toggleButtons = chartContainer.querySelectorAll('.chart-toggle');
        if (toggleButtons.length === 0) return;
        
        toggleButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                
                const viewType = button.getAttribute('data-chart');
                this.updateChart(chartId, rawData, viewType, toggleButtons);
            });
        });
        
        console.log(`Setup chart toggle for ${chartId} with ${toggleButtons.length} buttons`);
    }
    
    updateChart(chartId, rawData, viewType, toggleButtons) {
        const chart = this.charts.get(chartId);
        if (!chart) return;

        // Update button states
        toggleButtons.forEach(btn => btn.classList.remove('active'));
        const activeButton = Array.from(toggleButtons).find(btn => 
            btn.getAttribute('data-chart') === viewType
        );
        if (activeButton) activeButton.classList.add('active');

        // Update chart data
        chart.data = this.prepareChartData(rawData, viewType);
        chart.options = this.getChartOptions(viewType);
        chart.update('active');
        
        console.log(`Updated chart ${chartId} to ${viewType} view`);
    }
    
    setupEventListeners() {
        // Panel toggle functionality
        document.addEventListener('click', (e) => {
            if (e.target.matches('.panel-toggle') || e.target.closest('.panel-toggle')) {
                const toggle = e.target.closest('.panel-toggle');
                const panel = toggle.closest('.dashboard-panel');
                if (!panel) return;
                
                const content = panel.querySelector('.panel-content');
                const icon = toggle.querySelector('i');
                
                if (content && icon) {
                if (content.style.display === 'none') {
                    content.style.display = 'block';
                    icon.className = 'fas fa-chevron-up';
                    panel.classList.remove('collapsed');
                } else {
                    content.style.display = 'none';
                    icon.className = 'fas fa-chevron-down';
                    panel.classList.add('collapsed');
                }
            }
            }
        });

        // Responsive chart handling
        window.addEventListener('resize', this.debounce(() => {
            this.charts.forEach(chart => {
                if (chart && typeof chart.resize === 'function') {
                    chart.resize();
                }
            });
        }, 250));
    }
    
    debounce(func, wait) {
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
    
    // Public methods for external use
    refreshAllCharts() {
        this.charts.forEach(chart => {
            if (chart && typeof chart.update === 'function') {
                chart.update();
            }
        });
    }
    
    destroyAllCharts() {
        this.charts.forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts.clear();
    }
    
    getChartCount() {
        return this.charts.size;
    }
    
    // Debug method
    debugChartData() {
        console.log('=== GitHub Charts Debug ===');
        console.log('Charts created:', this.charts.size);
        console.log('Chart IDs:', Array.from(this.charts.keys()));
        
        // Check for chart data scripts
        const scriptElements = document.querySelectorAll('script[type="application/json"]');
        console.log('JSON data scripts found:', scriptElements.length);
        
        scriptElements.forEach(script => {
            console.log('Script ID:', script.id, 'Length:', script.textContent.length);
        });
    }
}

// Manual initialization - let templates control when to initialize
console.log('GitHub Charts Manager class loaded and ready');