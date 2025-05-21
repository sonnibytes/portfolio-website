/**
 * ML DEVLOG - Blog Navigation JavaScript
 * Interactive functionality for HUD-style blog navigation
 * Version: 1.1.0
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize blog sub-navigation functionality
  initSubNavigation();
  
  // Initialize search panel toggle
  initSearchPanel();
  
  // Initialize dropdown functionality
  initDropdowns();
});

// ===== SUB NAVIGATION FUNCTIONALITY =====
function initSubNavigation() {
  const subNavItems = document.querySelectorAll('.sub-nav-item');
  
  // Add hover effects and active state handling
  subNavItems.forEach(item => {
    // Skip dropdown toggles as they have their own handling
    if (item.classList.contains('dropdown-toggle')) {
      return;
    }
    
    item.addEventListener('mouseenter', function() {
      // Add glow effect or any other hover enhancements
      this.style.boxShadow = '0 0 10px rgba(0, 240, 255, 0.3)';
    });
    
    item.addEventListener('mouseleave', function() {
      // Remove hover effects
      this.style.boxShadow = '';
    });
  });
}

// ===== SEARCH PANEL FUNCTIONALITY =====
function initSearchPanel() {
  const searchToggle = document.getElementById('search-toggle');
  const searchPanel = document.getElementById('search-panel');
  
  if (searchToggle && searchPanel) {
    // Toggle search panel visibility
    searchToggle.addEventListener('click', function(e) {
      e.preventDefault();
      // Important: Stop propagation to prevent document click handler from firing
      e.stopPropagation();
      
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
    
    // Stop propagation on search panel clicks to prevent closing
    searchPanel.addEventListener('click', function(e) {
      e.stopPropagation();
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


// ===== DROPDOWN FUNCTIONALITY =====
function initDropdowns() {
  // Only initialize if Bootstrap's Dropdown implementation isn't available
  if (typeof bootstrap === 'undefined' || !bootstrap.Dropdown) {
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
      // Flag to track if dropdown is open
      let isDropdownOpen = false;
      
      // Get parent dropdown and its menu
      const dropdown = toggle.closest('.dropdown');
      const menu = dropdown.querySelector('.dropdown-menu');
      
      // Toggle on click
      toggle.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        // Toggle menu visibility
        if (menu.classList.contains('show')) {
          closeDropdown(menu);
          isDropdownOpen = false;
        } else {
          // Close all other open dropdowns
          document.querySelectorAll('.dropdown-menu.show').forEach(openMenu => {
            if (openMenu !== menu) {
              closeDropdown(openMenu);
            }
          });
          
          // Show this dropdown
          openDropdown(menu);
          isDropdownOpen = true;
        }
      });
      
      // Keep dropdown open when hovering over the menu
      if (window.innerWidth >= 992) { // Only on desktop
        menu.addEventListener('mouseenter', function() {
          isDropdownOpen = true;
        });
        
        menu.addEventListener('mouseleave', function() {
          // Small delay to allow moving to dropdown toggle
          setTimeout(() => {
            if (!toggle.matches(':hover')) {
              closeDropdown(menu);
              isDropdownOpen = false;
            }
          }, 200);
        });
        
        // Handle hover behavior for desktop
        toggle.addEventListener('mouseenter', function() {
          // Show dropdown menu
          openDropdown(menu);
        });
        
        // When moving away from toggle, check if we should close
        toggle.addEventListener('mouseleave', function() {
          // Small delay to allow moving to dropdown menu
          setTimeout(() => {
            if (!menu.matches(':hover')) {
              closeDropdown(menu);
            }
          }, 200);
        });
      }
      
      // Add click handlers to dropdown items
      const dropdownItems = menu.querySelectorAll('.dropdown-item');
      dropdownItems.forEach(item => {
        item.addEventListener('click', function(e) {
          // If item is a link with href, don't prevent default
          if (this.getAttribute('href') && this.getAttribute('href') !== '#') {
            // Allow time to see the active state before navigating
            e.preventDefault();
            const href = this.getAttribute('href');
            
            // Add active class
            this.classList.add('active');
            
            // Navigate after a slight delay
            setTimeout(() => {
              window.location.href = href;
            }, 150);
          }
          
          // Close dropdown after item click
          closeDropdown(menu);
          isDropdownOpen = false;
        });
      });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
      if (!e.target.closest('.dropdown')) {
        document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
          closeDropdown(menu);
        });
      }
    });
  } else {
    // Bootstrap dropdowns are active, but we still need to fix some behavior
    const dropdownMenus = document.querySelectorAll('.dropdown-menu');
    
    // Add hover persistence for desktop
    if (window.innerWidth >= 992) {
      dropdownMenus.forEach(menu => {
        const parentDropdown = menu.closest('.dropdown');
        const toggle = parentDropdown.querySelector('.dropdown-toggle');
        
        // Keep dropdown open when hovering over the menu
        menu.addEventListener('mouseenter', function() {
          parentDropdown.classList.add('show');
          menu.classList.add('show');
          toggle.setAttribute('aria-expanded', 'true');
        });
        
        menu.addEventListener('mouseleave', function() {
          // Small delay to allow moving to dropdown toggle
          setTimeout(() => {
            if (!toggle.matches(':hover')) {
              parentDropdown.classList.remove('show');
              menu.classList.remove('show');
              toggle.setAttribute('aria-expanded', 'false');
            }
          }, 200);
        });
        
        // When moving away from toggle, check if we should close
        toggle.addEventListener('mouseleave', function() {
          // Small delay to allow moving to dropdown menu
          setTimeout(() => {
            if (!menu.matches(':hover')) {
              parentDropdown.classList.remove('show');
              menu.classList.remove('show');
              toggle.setAttribute('aria-expanded', 'false');
            }
          }, 200);
        });
      });
    }
    
    // Add active class to dropdown items on click
    const dropdownItems = document.querySelectorAll('.dropdown-menu .dropdown-item');
    dropdownItems.forEach(item => {
      item.addEventListener('click', function() {
        // If item has href, add active class
        if (this.getAttribute('href') && this.getAttribute('href') !== '#') {
          this.classList.add('active');
        }
      });
    });
  }
}

// Helper function to open dropdown
function openDropdown(menu) {
  menu.classList.add('show');
  const toggle = menu.previousElementSibling;
  if (toggle && toggle.classList.contains('dropdown-toggle')) {
    toggle.setAttribute('aria-expanded', 'true');
    toggle.classList.add('active');
  }
}

// Helper function to close dropdown
function closeDropdown(menu) {
  menu.classList.remove('show');
  const toggle = menu.previousElementSibling;
  if (toggle && toggle.classList.contains('dropdown-toggle')) {
    toggle.setAttribute('aria-expanded', 'false');
    toggle.classList.remove('active');
  }
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