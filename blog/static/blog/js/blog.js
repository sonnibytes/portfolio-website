/**
 * ML DEVLOG - Blog JavaScript
 * Simplified to only include copy functionality (Pygments handles highlighting)
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add copy code functionality
    function addCopyButtons() {
        const codeBlocks = document.querySelectorAll('.code-block');
        
        codeBlocks.forEach(block => {
            const header = block.querySelector('.code-header');
            if (header) {
                const copyButton = document.createElement('button');
                copyButton.className = 'copy-button';
                copyButton.innerHTML = '<i class="fas fa-copy"></i>';
                copyButton.title = 'Copy code';
                copyButton.style.marginLeft = 'auto';
                copyButton.style.background = 'transparent';
                copyButton.style.border = 'none';
                copyButton.style.color = '#808080';
                copyButton.style.cursor = 'pointer';
                copyButton.style.fontSize = '14px';
                
                copyButton.addEventListener('click', () => {
                    const codeContent = block.querySelector('.code-content');
                    if (codeContent) {
                        // Get the text content from the code element
                        // This works for both Pygments-highlighted code and plain text
                        const pre = codeContent.querySelector('pre');
                        const textToCopy = pre ? pre.textContent : codeContent.textContent;
                        
                        navigator.clipboard.writeText(textToCopy).then(() => {
                            copyButton.innerHTML = '<i class="fas fa-check"></i>';
                            copyButton.style.color = '#27c93f';
                            
                            setTimeout(() => {
                                copyButton.innerHTML = '<i class="fas fa-copy"></i>';
                                copyButton.style.color = '#808080';
                            }, 2000);
                        }).catch(err => {
                            console.error('Failed to copy text: ', err);
                            copyButton.innerHTML = '<i class="fas fa-times"></i>';
                            copyButton.style.color = '#ff5f56';
                            
                            setTimeout(() => {
                                copyButton.innerHTML = '<i class="fas fa-copy"></i>';
                                copyButton.style.color = '#808080';
                            }, 2000);
                        });
                    }
                });
                
                header.appendChild(copyButton);
            }
        });
    }
    
    // Initialize the copy functionality
    addCopyButtons();
});

// Initialize Bootstrap dropdowns
document.addEventListener('DOMContentLoaded', function() {
    var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
    var dropdownList = dropdownElementList.map(function (dropdownToggleEl) {
      return new bootstrap.Dropdown(dropdownToggleEl);
    });
    
    // For desktop: Show dropdown on hover
    var dropdownHoverElements = document.querySelectorAll('.dropdown');
    
    dropdownHoverElements.forEach(function(element) {
      element.addEventListener('mouseenter', function() {
        if (window.innerWidth >= 992) { // Only on desktop
          var dropdownToggle = this.querySelector('.dropdown-toggle');
          var dropdown = bootstrap.Dropdown.getInstance(dropdownToggle);
          if (dropdown) {
            dropdown.show();
          }
        }
      });
      
      element.addEventListener('mouseleave', function() {
        if (window.innerWidth >= 992) { // Only on desktop
          var dropdownToggle = this.querySelector('.dropdown-toggle');
          var dropdown = bootstrap.Dropdown.getInstance(dropdownToggle);
          if (dropdown) {
            dropdown.hide();
          }
        }
      });
    });
  });