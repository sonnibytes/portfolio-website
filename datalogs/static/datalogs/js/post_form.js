/**
 * ML DEVLOG - Post Form JavaScript
 * Functionality for the blog post creation and editing form
 */

document.addEventListener('DOMContentLoaded', function() {
    // ===== FORM SECTION MANAGEMENT =====
    
    // Get form elements
    const featuredCheckbox = document.getElementById('id_featured');
    const featuredCodeSection = document.querySelector('.featured-code-section');
    
    // Toggle featured code section visibility based on featured checkbox
    if (featuredCheckbox && featuredCodeSection) {
      // Initial state
      featuredCodeSection.style.display = featuredCheckbox.checked ? 'block' : 'none';
      
      // Toggle on change
      featuredCheckbox.addEventListener('change', function() {
        featuredCodeSection.style.display = this.checked ? 'block' : 'none';
      });
    }
    
    // Toggle raw markdown editor
    const toggleRawMarkdown = document.getElementById('toggle-raw-markdown');
    const rawMarkdownContainer = document.getElementById('raw-markdown-container');
    
    if (toggleRawMarkdown && rawMarkdownContainer) {
      toggleRawMarkdown.addEventListener('change', function() {
        rawMarkdownContainer.style.display = this.checked ? 'block' : 'none';
      });
    }
    
    // Hide empty sections initially
    const contentSections = document.querySelectorAll('.content-section');
    let visibleSections = 1; // Always show at least section 1
    
    contentSections.forEach((section, index) => {
      const titleInput = section.querySelector('input[id$="_title"]');
      const contentTextarea = section.querySelector('textarea[id$="_content"]');
      
      if (index > 0) { // Skip section 1
        if ((titleInput && titleInput.value) || (contentTextarea && contentTextarea.value)) {
          visibleSections = index + 1;
        } else {
          section.style.display = 'none';
        }
      }
    });
    
    // Add "Add Section" button after the last visible section
    const lastVisibleSection = document.getElementById(`section-${visibleSections}`);
    if (lastVisibleSection && visibleSections < 5) {
      const addButton = document.createElement('button');
      addButton.type = 'button';
      addButton.className = 'btn btn-outline-cyan mt-3 mb-4';
      addButton.textContent = 'Add Section';
      addButton.addEventListener('click', function() {
        if (visibleSections < 5) {
          document.getElementById(`section-${visibleSections + 1}`).style.display = 'block';
          visibleSections++;
          
          // Move button after newly visible section
          if (visibleSections < 5) {
            this.parentNode.removeChild(this);
            document.getElementById(`section-${visibleSections}`).after(this);
          } else {
            this.parentNode.removeChild(this);
          }
        }
      });
      
      lastVisibleSection.after(addButton);
    }
    
    // ===== PREVIEW FUNCTIONALITY =====
    
    const togglePreviewBtn = document.getElementById('toggle-preview');
    const previewSection = document.getElementById('post-preview');
    const previewTitle = document.getElementById('preview-post-title');
    const previewBody = document.querySelector('.preview-body');
    const previewReadingTime = document.getElementById('preview-reading-time');
    
    if (togglePreviewBtn && previewSection) {
      togglePreviewBtn.addEventListener('click', function() {
        if (previewSection.style.display === 'none') {
          updatePreview();
          previewSection.style.display = 'block';
          togglePreviewBtn.innerHTML = '<i class="fas fa-eye-slash me-1"></i> Hide Preview';
          
          // Scroll to preview
          setTimeout(() => {
            previewSection.scrollIntoView({ behavior: 'smooth' });
          }, 100);
        } else {
          previewSection.style.display = 'none';
          togglePreviewBtn.innerHTML = '<i class="fas fa-eye me-1"></i> Toggle Preview';
        }
      });
      
      // Update preview when content changes
      const formInputs = document.querySelectorAll('input, textarea, select');
      formInputs.forEach(input => {
        input.addEventListener('change', updatePreview);
        if (input.tagName === 'TEXTAREA') {
          input.addEventListener('keyup', debounce(updatePreview, 500));
        }
      });
    }
    
    function updatePreview() {
      // If preview section is not visible, don't update
      if (previewSection && previewSection.style.display === 'none') {
        return;
      }
      
      // Update title
      const titleInput = document.getElementById('id_title');
      previewTitle.textContent = titleInput.value || 'Post Title';
      
      // Build markdown content
      let markdownContent = '';
      
      // Introduction
      const introInput = document.getElementById('id_introduction');
      if (introInput && introInput.value) {
        markdownContent += introInput.value + '\n\n';
      }
      
      // Sections
      for (let i = 1; i <= 5; i++) {
        const titleInput = document.querySelector(`[id$=section_${i}_title]`);
        const contentInput = document.querySelector(`[id$=section_${i}_content]`);
        
        if (titleInput && contentInput && titleInput.value) {
          markdownContent += `## ${titleInput.value}\n\n`;
          if (contentInput.value) {
            markdownContent += contentInput.value + '\n\n';
          }
        }
      }
      
      // Code snippet
      const codeInput = document.getElementById('id_code_snippet');
      const langInput = document.getElementById('id_code_language');
      
      if (codeInput && langInput && codeInput.value) {
        markdownContent += '```' + langInput.value + '\n';
        markdownContent += codeInput.value + '\n';
        markdownContent += '```\n\n';
      }
      
      // Conclusion
      const conclusionInput = document.getElementById('id_conclusion');
      if (conclusionInput && conclusionInput.value) {
        markdownContent += '## Conclusion\n\n';
        markdownContent += conclusionInput.value + '\n\n';
      }
      
      // Raw markdown override
      const toggleRawMd = document.getElementById('toggle-raw-markdown');
      const rawMdInput = document.getElementById('id_content');
      
      if (toggleRawMd && toggleRawMd.checked && rawMdInput && rawMdInput.value) {
        markdownContent = rawMdInput.value;
      }
      
      // Convert markdown to HTML
      fetch('/markdownx/markdownify/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': getCsrfToken(),
        },
        body: 'content=' + encodeURIComponent(markdownContent)
      })
      .then(response => response.json())
      .then(data => {
        previewBody.innerHTML = data.content;
        
        // Update reading time (very rough estimate)
        const wordCount = markdownContent.split(/\s+/).length;
        previewReadingTime.textContent = Math.max(1, Math.round(wordCount / 200));
        
        // Syntax highlight code blocks
        if (window.hljs) {
          document.querySelectorAll('pre code').forEach(block => {
            hljs.highlightElement(block);
          });
        }
      });
    }
    
    // ===== AUTO-SAVE FUNCTIONALITY =====
    
    // Get post ID from URL or use 'new' if creating a new post
    const postId = window.location.pathname.includes('edit') ? 
      window.location.pathname.split('/').filter(Boolean).pop() : 'new';
    
    const autoSaveKey = `blog_post_autosave_${postId}`;
    const autoSaveStatus = document.createElement('div');
    autoSaveStatus.className = 'auto-save-status';
    autoSaveStatus.innerHTML = '<i class="fas fa-sync"></i> Auto-save ready';
    
    const formActions = document.querySelector('.form-actions');
    if (formActions) {
      formActions.appendChild(autoSaveStatus);
      
      // Load auto-saved content
      loadAutoSavedContent();
      
      // Set up auto-save interval
      setInterval(autoSaveContent, 60000); // Auto-save every minute
    }
    
    // Load auto-saved content
    function loadAutoSavedContent() {
      const savedData = localStorage.getItem(autoSaveKey);
      if (savedData) {
        try {
          const data = JSON.parse(savedData);
          const timestamp = new Date(data.timestamp);
          const now = new Date();
          const diff = Math.floor((now - timestamp) / 1000 / 60); // Minutes
          
          // Only restore if less than 1 day old
          if (diff < 1440) {
            // Ask user if they want to restore
            if (confirm(`Restore auto-saved draft from ${diff < 60 ? diff + ' minutes' : Math.floor(diff/60) + ' hours'} ago?`)) {
              // Restore form data
              Object.keys(data.formData).forEach(key => {
                const input = document.querySelector(`[name="${key}"]`);
                if (input) {
                  if (input.type === 'checkbox') {
                    input.checked = data.formData[key] === 'true';
                  } else if (input.tagName === 'SELECT' && input.multiple) {
                    // Handle multi-select
                    const values = data.formData[key].split(',');
                    Array.from(input.options).forEach(option => {
                      option.selected = values.includes(option.value);
                    });
                  } else {
                    input.value = data.formData[key];
                  }
                }
              });
              
              // Update UI
              if (featuredCheckbox) {
                featuredCodeSection.style.display = featuredCheckbox.checked ? 'block' : 'none';
              }
              
              autoSaveStatus.innerHTML = '<i class="fas fa-check-circle"></i> Restored auto-saved draft';
              autoSaveStatus.classList.add('restored');
              
              setTimeout(() => {
                autoSaveStatus.classList.remove('restored');
              }, 3000);
            }
          } else {
            // Clear old autosave
            localStorage.removeItem(autoSaveKey);
          }
        } catch (e) {
          console.error('Error loading auto-saved content', e);
          localStorage.removeItem(autoSaveKey);
        }
      }
    }
    
    // Auto-save form content
    function autoSaveContent() {
      const form = document.querySelector('form.structured-form');
      if (!form) return;
      
      const formData = {};
      const formElements = form.elements;
      
      for (let i = 0; i < formElements.length; i++) {
        const element = formElements[i];
        if (element.name && element.name !== 'csrfmiddlewaretoken') {
          if (element.type === 'checkbox') {
            formData[element.name] = element.checked.toString();
          } else if (element.tagName === 'SELECT' && element.multiple) {
            const selectedValues = Array.from(element.selectedOptions).map(option => option.value).join(',');
            formData[element.name] = selectedValues;
          } else {
            formData[element.name] = element.value;
          }
        }
      }
      
      const saveData = {
        formData: formData,
        timestamp: new Date().toISOString()
      };
      
      localStorage.setItem(autoSaveKey, JSON.stringify(saveData));
      
      // Update status
      autoSaveStatus.innerHTML = '<i class="fas fa-check-circle"></i> Auto-saved';
      autoSaveStatus.classList.add('saved');
      
      setTimeout(() => {
        autoSaveStatus.classList.remove('saved');
        autoSaveStatus.innerHTML = '<i class="fas fa-sync"></i> Auto-save ready';
      }, 2000);
    }
    
    // Set up auto-save on input changes
    const formInputs = document.querySelectorAll('input, textarea, select');
    formInputs.forEach(input => {
      input.addEventListener('change', () => {
        clearTimeout(autoSaveTimer);
        autoSaveTimer = setTimeout(autoSaveContent, 1000);
      });
      
      if (input.tagName === 'TEXTAREA') {
        input.addEventListener('keyup', () => {
          clearTimeout(autoSaveTimer);
          autoSaveTimer = setTimeout(autoSaveContent, 3000);
        });
      }
    });
    
    let autoSaveTimer;
    
    // ===== IMAGE UPLOAD HANDLING =====
    
    const dropZone = document.getElementById('image-drop-zone');
    const imageUpload = document.getElementById('image-upload');
    const imagePreviewContainer = document.querySelector('.image-preview-container');
    const imagePreview = document.querySelector('.image-preview');
    const imageMarkdownLink = document.getElementById('image-markdown-link');
    const copyImageLinkBtn = document.getElementById('copy-image-link');
    
    if (dropZone && imageUpload) {
      // Handle click on drop zone
      dropZone.addEventListener('click', () => {
        imageUpload.click();
      });
      
      // Handle file select
      imageUpload.addEventListener('change', function() {
        if (this.files && this.files[0]) {
          handleImageUpload(this.files[0]);
        }
      });
      
      // Handle drag and drop
      ['dragover', 'dragenter'].forEach(eventName => {
        dropZone.addEventListener(eventName, e => {
          e.preventDefault();
          dropZone.classList.add('drag-over');
        });
      });
      
      ['dragleave', 'dragend'].forEach(eventName => {
        dropZone.addEventListener(eventName, e => {
          e.preventDefault();
          dropZone.classList.remove('drag-over');
        });
      });
      
      dropZone.addEventListener('drop', e => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
          handleImageUpload(e.dataTransfer.files[0]);
        }
      });
      
      // Copy markdown link
      if (copyImageLinkBtn) {
        copyImageLinkBtn.addEventListener('click', () => {
          imageMarkdownLink.select();
          document.execCommand('copy');
          
          // Show feedback
          const originalText = copyImageLinkBtn.innerHTML;
          copyImageLinkBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
          
          setTimeout(() => {
            copyImageLinkBtn.innerHTML = originalText;
          }, 2000);
        });
      }
    }
    
    // Function to handle image upload
    function handleImageUpload(file) {
      // Check if file is an image
      if (!file.type.match('image.*')) {
        alert('Please select an image file');
        return;
      }
      
      // Create form data
      const formData = new FormData();
      formData.append('image', file);
      formData.append('csrfmiddlewaretoken', getCsrfToken());
      
      // Show loading state
      dropZone.innerHTML = '<div class="spinner-border text-info" role="status"><span class="visually-hidden">Loading...</span></div>';
      
      // Upload the file
      fetch('/blog/upload/image/', {
        method: 'POST',
        body: formData,
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        // Show the image preview
        imagePreview.innerHTML = `<img src="${data.url}" alt="${file.name}" class="img-fluid">`;
        imagePreviewContainer.style.display = 'block';
        
        // Set the markdown link
        imageMarkdownLink.value = `![${file.name}](${data.url})`;
        
        // Reset drop zone
        dropZone.innerHTML = `
          <div class="drop-zone-icon">
            <i class="fas fa-cloud-upload-alt"></i>
          </div>
          <div class="drop-zone-prompt">Drag & drop an image or click to browse</div>
        `;
      })
      .catch(error => {
        console.error('Error uploading image:', error);
        dropZone.innerHTML = `
          <div class="drop-zone-icon text-danger">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <div class="drop-zone-prompt text-danger">Error uploading image. Please try again.</div>
        `;
      });
    }
    
    // ===== TAGS INPUT ENHANCEMENT =====
    
    const tagInput = document.getElementById('tag-input');
    const selectedTags = document.getElementById('selected-tags');
    const tagsHiddenInput = document.getElementById('id_tags');
    let currentTags = [];
    
    // Initialize from existing tags (for edit mode)
    if (tagsHiddenInput && tagsHiddenInput.value) {
      const selectedOptions = Array.from(tagsHiddenInput.selectedOptions || []);
      currentTags = selectedOptions.map(option => ({
        id: option.value,
        name: option.text
      }));
      
      renderTags();
    }
    
    if (tagInput && selectedTags && tagsHiddenInput) {
      // Create suggestions container
      const suggestionsContainer = document.createElement('div');
      suggestionsContainer.className = 'tag-suggestions';
      suggestionsContainer.style.display = 'none';
      tagInput.parentNode.style.position = 'relative';
      tagInput.parentNode.appendChild(suggestionsContainer);
      
      // Handle tag input
      tagInput.addEventListener('input', debounce(function() {
        const query = this.value.trim();
        if (query.length < 2) {
          suggestionsContainer.style.display = 'none';
          return;
        }
        
        // Fetch tag suggestions
        fetch(`/blog/tags/suggestions/?q=${encodeURIComponent(query)}`)
          .then(response => response.json())
          .then(data => {
            if (data.tags && data.tags.length > 0) {
              // Filter out already selected tags
              const availableTags = data.tags.filter(tag => 
                !currentTags.some(t => t.id === tag.id)
              );
              
              if (availableTags.length > 0) {
                // Render suggestions
                suggestionsContainer.innerHTML = availableTags.map(tag => 
                  `<div class="tag-suggestion" data-id="${tag.id}" data-name="${tag.name}">${tag.name}</div>`
                ).join('');
                
                suggestionsContainer.style.display = 'block';
                
                // Add click handlers for suggestions
                document.querySelectorAll('.tag-suggestion').forEach(suggestion => {
                  suggestion.addEventListener('click', function() {
                    const tagId = this.dataset.id;
                    const tagName = this.dataset.name;
                    
                    addTag(tagId, tagName);
                    tagInput.value = '';
                    suggestionsContainer.style.display = 'none';
                    tagInput.focus();
                  });
                });
              } else {
                suggestionsContainer.style.display = 'none';
              }
            } else {
              suggestionsContainer.style.display = 'none';
            }
          });
      }, 300));
      
      // Handle enter key to add a new tag
      tagInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && this.value.trim()) {
          e.preventDefault();
          
          // Check if there's a visible suggestion
          const firstSuggestion = suggestionsContainer.querySelector('.tag-suggestion');
          if (firstSuggestion && suggestionsContainer.style.display !== 'none') {
            // Use the first suggestion
            const tagId = firstSuggestion.dataset.id;
            const tagName = firstSuggestion.dataset.name;
            addTag(tagId, tagName);
          } else {
            // Create new tag
            createNewTag(this.value.trim());
          }
          
          this.value = '';
          suggestionsContainer.style.display = 'none';
        }
      });
      
      // Hide suggestions when clicking outside
      document.addEventListener('click', function(e) {
        if (!tagInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
          suggestionsContainer.style.display = 'none';
        }
      });
    }
    
    // Function to add a tag
    function addTag(id, name) {
      if (!currentTags.some(tag => tag.id === id)) {
        currentTags.push({ id, name });
        renderTags();
        updateHiddenInput();
      }
    }
    
    // Function to create a new tag
    function createNewTag(name) {
      // Check if tag already exists with this name
      if (currentTags.some(tag => tag.name.toLowerCase() === name.toLowerCase())) {
        return;
      }
      
      // Create new tag on server
      fetch('/blog/tags/create/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({ name: name })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          addTag(data.tag.id, data.tag.name);
        }
      });
    }
    
    // Function to render tags
    function renderTags() {
      if (!selectedTags) return;
      
      selectedTags.innerHTML = '';
      
      currentTags.forEach(tag => {
        const tagElement = document.createElement('span');
        tagElement.className = 'selected-tag';
        tagElement.innerHTML = `
          ${tag.name}
          <span class="remove-tag" data-id="${tag.id}">×</span>
        `;
        selectedTags.appendChild(tagElement);
        
        // Add click handler for remove button
        tagElement.querySelector('.remove-tag').addEventListener('click', function() {
          const tagId = this.dataset.id;
          removeTag(tagId);
        });
      });
    }
    
    // Function to remove a tag
    function removeTag(id) {
      currentTags = currentTags.filter(tag => tag.id !== id);
      renderTags();
      updateHiddenInput();
    }
    
    // Function to update hidden input
    function updateHiddenInput() {
      if (!tagsHiddenInput) return;
      
      // Clear all selections
      Array.from(tagsHiddenInput.options).forEach(option => {
        option.selected = false;
      });
      
      // Set selected options based on currentTags
      currentTags.forEach(tag => {
        const option = Array.from(tagsHiddenInput.options).find(opt => opt.value === tag.id);
        if (option) {
          option.selected = true;
        } else {
          // If option doesn't exist, create it
          const newOption = new Option(tag.name, tag.id, true, true);
          tagsHiddenInput.appendChild(newOption);
        }
      });
    }
    
    // ===== UTILITY FUNCTIONS =====
    
    // Helper to get CSRF token
    function getCsrfToken() {
      return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
    
    // Debounce function to limit how often a function is called
    function debounce(func, wait) {
      let timeout;
      return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
          func.apply(context, args);
        }, wait);
      };
    }
  });