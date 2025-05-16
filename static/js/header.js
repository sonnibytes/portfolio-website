
// Header JavaScript for ML DEVLOG
document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle functionality
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
            this.classList.toggle('active');
        });
    }
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        if (mobileMenu?.classList.contains('active') && 
            !mobileMenu.contains(event.target) && 
            !mobileMenuButton.contains(event.target)) {
            mobileMenu.classList.remove('active');
            mobileMenuButton.classList.remove('active');
        }
    });
    
    // Change header on scroll
    const header = document.querySelector('.site-header');
    
    if (header) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }
});