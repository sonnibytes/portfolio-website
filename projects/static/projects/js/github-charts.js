// projects/static/projects/js/github-charts.js
// GitHub Charts Manager - Assumes Chart.js is globally loaded

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
        
        // Set global defaults for AURA theme
        this.setGlobalDefaults();
        
        // Initialize all charts on page
        this.initializeCharts();
        
        // Setup event listeners
        this.setupEventListeners();
    }
    
    setGlobalDefaults() {
        Chart.defaults.color = this.colors.text;
        Chart.defaults.borderColor = this.colors.grid;
        Chart.defaults.backgroundColor = this.colors.background;
    }
    
    initializeCharts() {
        const chartElements = document.querySelectorAll('.commit-chart');
        console.log(`Found ${chartElements.length} GitHub charts to initialize`);
        
        chartElements.forEach(canvas => {
            try {
                const chartData = JSON.parse(canvas.getAttribute('data-chart-data'));
                const chartId = canvas.id;
                
                if (chartData && chartData.labels && chartData.labels.length > 0) {
                    this.createCommitChart(canvas, chartData, chartId);
                } else {
                    console.warn('No chart data for', chartId);
                }
            } catch (error) {
                console.warn('Failed to initialize chart:', canvas.id, error);
            }
        });
    }
    
    createCommitChart(canvas, data, chartId) {
        const ctx = canvas.getContext('2d');
        
        const config = {
            type: 'line',
            data: this.prepareChartData(data, 'weekly'),
            options: this.getChartOptions('weekly')
        };

        // Create chart
        const chart = new Chart(ctx, config);
        this.charts.set(chartId, chart);
        
        // Setup toggle functionality
        this.setupChartToggle(chartId, data);
        
        console.log('✅ Created GitHub chart:', chartId);
    }
    
    prepareChartData(rawData, viewType = 'weekly') {
        const isWeekly = viewType === 'weekly';
        const labels = isWeekly ? rawData.labels : rawData.monthly_labels;
        const commits = isWeekly ? rawData.weekly : rawData.monthly;

        return {
            labels: labels || [],
            datasets: [{
                label: isWeekly ? 'Weekly Commits' : 'Monthly Commits',
                data: commits || [],
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
        return {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: { display: false },
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
                            const period = viewType === 'weekly' ? 'week' : 'month';
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
                        font: { size: 11 },
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
                        font: { size: 11 },
                        stepSize: 1,
                        callback: function(value) {
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
        
        toggleButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                
                const viewType = button.getAttribute('data-chart');
                this.updateChart(chartId, rawData, viewType, toggleButtons);
            });
        });
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
                const content = panel.querySelector('.panel-content');
                const icon = toggle.querySelector('i');
                
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
        });

        // Responsive chart handling
        window.addEventListener('resize', this.debounce(() => {
            this.charts.forEach(chart => chart.resize());
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
        this.charts.forEach(chart => chart.update());
    }
    
    destroyAllCharts() {
        this.charts.forEach(chart => chart.destroy());
        this.charts.clear();
    }
}

// Auto-initialize if Chart.js is available
document.addEventListener('DOMContentLoaded', function() {
    if (typeof Chart !== 'undefined' && document.querySelectorAll('.commit-chart').length > 0) {
        window.githubCharts = new GitHubChartsManager();
    }
});