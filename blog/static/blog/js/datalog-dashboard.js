// admin dashboard js
// blog/static/blog/js/datalog-dashboard.js
document.addEventListener('DOMContentLoaded', function() {
    initializeDatalogDashboard();
});

function initializeDatalogDashboard() {
    // Initialize quick stats animation
    animateStats();
    
    // Initialize search functionality
    initializeDashboardSearch();
    
    // Initialize status filters
    initializeStatusFilters();
}

function animateStats() {
    const statValues = document.querySelectorAll('.stat-value');
    
    statValues.forEach(stat => {
        const finalValue = parseInt(stat.textContent);
        let currentValue = 0;
        const increment = Math.ceil(finalValue / 20);
        
        const animation = setInterval(() => {
            currentValue += increment;
            if (currentValue >= finalValue) {
                currentValue = finalValue;
                clearInterval(animation);
            }
            stat.textContent = currentValue;
        }, 50);
    });
}

function initializeDashboardSearch() {
    const searchInput = document.querySelector('.dashboard-search');
    if (!searchInput) return;
    
    const postItems = document.querySelectorAll('.post-item');
    
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase();
        
        postItems.forEach(item => {
            const title = item.querySelector('.post-title').textContent.toLowerCase();
            const isVisible = title.includes(query);
            item.style.display = isVisible ? 'block' : 'none';
        });
    });
}

function initializeStatusFilters() {
    const filterButtons = document.querySelectorAll('.status-filter');
    const postItems = document.querySelectorAll('.post-item');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const status = this.dataset.status;
            
            // Update active filter
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Filter posts
            postItems.forEach(item => {
                const postStatus = item.querySelector('.post-status').textContent.toLowerCase();
                const isVisible = status === 'all' || postStatus.includes(status);
                item.style.display = isVisible ? 'block' : 'none';
            });
        });
    });
}