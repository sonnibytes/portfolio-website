// Initialize all functionality when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Search panel toggle
    const searchToggle = document.getElementById('search-toggle');
    const searchPanel = document.getElementById('search-panel');
    
    if (searchToggle && searchPanel) {
      searchToggle.addEventListener('click', function(e) {
        e.preventDefault();
        searchPanel.style.display = searchPanel.style.display === 'none' ? 'block' : 'none';
        if (searchPanel.style.display === 'block') {
          searchPanel.querySelector('input').focus();
        }
      });
    }
    
    // For desktop: Enable hover behavior for dropdowns
    const dropdowns = document.querySelectorAll('.dropdown');
    
    if (window.innerWidth >= 992) { // Only on desktop
      dropdowns.forEach(function(dropdown) {
        const dropdownMenu = dropdown.querySelector('.dropdown-menu');
        
        dropdown.addEventListener('mouseenter', function() {
          if (dropdownMenu) {
            dropdownMenu.classList.add('show');
          }
        });
        
        dropdown.addEventListener('mouseleave', function() {
          if (dropdownMenu) {
            dropdownMenu.classList.remove('show');
          }
        });
      });
    }
    
    // Initialize Bootstrap dropdowns
    try {
      var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
      var dropdownList = dropdownElementList.map(function(dropdownToggleEl) {
        return new bootstrap.Dropdown(dropdownToggleEl);
      });
    } catch (e) {
      console.warn('Bootstrap dropdown initialization failed. Bootstrap may not be loaded.');
    }
  });