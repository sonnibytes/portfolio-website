/**
 * ML DEVLOG - Blog JavaScript
 * Enhances the blog with interactive features and animations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize syntax highlighting with Prism.js
    Prism.highlightAll();
    
    // Add smooth scrolling for table of contents links
    const tocLinks = document.querySelectorAll('.toc-link');
    
    tocLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 100,
                    behavior: 'smooth'
                });
                
                // Add highlight effect to the target heading
                targetElement.classList.add('highlight');
                
                setTimeout(() => {
                    targetElement.classList.remove('highlight');
                }, 2000);
            }
        });
    });
    
    // Add code copy button functionality
    const codeBlocks = document.querySelectorAll('.code-block');
    
    codeBlocks.forEach(block => {
        // Create copy button
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.innerHTML = '<i class="fas fa-copy"></i>';
        copyButton.title = 'Copy code';
        
        // Add button to code header
        const codeHeader = block.querySelector('.code-header');
        codeHeader.appendChild(copyButton);
        
        // Add click event
        copyButton.addEventListener('click', () => {
            const codeContent = block.querySelector('code').textContent;
            
            // Copy to clipboard
            navigator.clipboard.writeText(codeContent)
                .then(() => {
                    // Show success message
                    copyButton.innerHTML = '<i class="fas fa-check"></i>';
                    copyButton.classList.add('copied');
                    
                    // Reset after 2 seconds
                    setTimeout(() => {
                        copyButton.innerHTML = '<i class="fas fa-copy"></i>';
                        copyButton.classList.remove('copied');
                    }, 2000);
                })
                .catch(err => {
                    console.error('Could not copy text: ', err);
                });
        });
    });
    
    // Add scroll animations for post cards
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    const postCards = document.querySelectorAll('.post-card');
    
    postCards.forEach(card => {
        card.classList.add('pre-animation');
        observer.observe(card);
    });
    
    // Add active states to navigation
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        
        if (currentPath.includes('/blog/') && linkPath.includes('/blog/')) {
            link.classList.add('active');
        } else if (currentPath === linkPath) {
            link.classList.add('active');
        }
    });
    
    // Handle mobile navigation
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('active');
            mobileMenuButton.classList.toggle('active');
        });
    }
    
    // Add reading progress bar
    const progressBar = document.createElement('div');
    progressBar.className = 'reading-progress';
    document.body.appendChild(progressBar);
    
    if (document.querySelector('.post-content')) {
        window.addEventListener('scroll', () => {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            
            progressBar.style.width = scrolled + '%';
        });
    }
    
    // Add estimated reading time calculator
    const postContent = document.querySelector('.post-content');
    const readingTimeElement = document.querySelector('.reading-time');
    
    if (postContent && readingTimeElement && !readingTimeElement.textContent.trim()) {
        const text = postContent.textContent;
        const wordCount = text.split(/\s+/).length;
        const readingTime = Math.ceil(wordCount / 200); // Average reading speed: 200 words per minute
        
        readingTimeElement.textContent = readingTime + ' min read';
    }
    
    // Add category color variables to post cards
    const categoryElements = document.querySelectorAll('[class*="category-"]');
    
    categoryElements.forEach(el => {
        const classes = el.className.split(' ');
        const categoryClass = classes.find(c => c.startsWith('category-'));
        
        if (categoryClass) {
            const categorySlug = categoryClass.replace('category-', '');
            const colorMap = {
                'ml': 'var(--color-cyan)',
                'py': 'var(--color-purple)',
                'ds': '#00ff9d',
                'ai': '#ff5e94',
                'jn': '#ffcc00',
                'wd': '#00e5ff'
            };
            
            el.style.setProperty('--category-color', colorMap[categorySlug] || 'var(--color-cyan)');
        }
    });
});