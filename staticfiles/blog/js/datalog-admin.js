// blog/static/blog/js/datalog-admin.js
function initializeMarkdownEditor() {
    const contentField = document.querySelector('#id_content');
    if (!contentField) return;
    
    // Add markdown toolbar
    addMarkdownToolbar(contentField);
    
    // Enable tab support
    enableTabSupport(contentField);
    
    // Add live preview
    addLivePreview(contentField);
}

function addMarkdownToolbar(textarea) {
    const toolbar = document.createElement('div');
    toolbar.className = 'markdown-toolbar';
    toolbar.innerHTML = `
        <button type="button" class="md-btn" data-action="bold" title="Bold">
            <i class="fas fa-bold"></i>
        </button>
        <button type="button" class="md-btn" data-action="italic" title="Italic">
            <i class="fas fa-italic"></i>
        </button>
        <button type="button" class="md-btn" data-action="code" title="Code">
            <i class="fas fa-code"></i>
        </button>
        <button type="button" class="md-btn" data-action="link" title="Link">
            <i class="fas fa-link"></i>
        </button>
        <button type="button" class="md-btn" data-action="heading" title="Heading">
            <i class="fas fa-heading"></i>
        </button>
        <button type="button" class="md-btn" data-action="list" title="List">
            <i class="fas fa-list-ul"></i>
        </button>
        <button type="button" class="md-btn" data-action="quote" title="Quote">
            <i class="fas fa-quote-left"></i>
        </button>
    `;
    
    textarea.parentNode.insertBefore(toolbar, textarea);
    
    toolbar.addEventListener('click', function(e) {
        const button = e.target.closest('.md-btn');
        if (button) {
            e.preventDefault();
            handleMarkdownAction(textarea, button.dataset.action);
        }
    });
}

function handleMarkdownAction(textarea, action) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    
    let replacement = '';
    
    switch (action) {
        case 'bold':
            replacement = `**${selectedText || 'bold text'}**`;
            break;
        case 'italic':
            replacement = `*${selectedText || 'italic text'}*`;
            break;
        case 'code':
            replacement = selectedText.includes('\n') 
                ? `\`\`\`\n${selectedText || 'code block'}\n\`\`\``
                : `\`${selectedText || 'code'}\``;
            break;
        case 'link':
            replacement = `[${selectedText || 'link text'}](url)`;
            break;
        case 'heading':
            replacement = `## ${selectedText || 'Heading'}`;
            break;
        case 'list':
            replacement = selectedText 
                ? selectedText.split('\n').map(line => `- ${line}`).join('\n')
                : '- List item';
            break;
        case 'quote':
            replacement = selectedText 
                ? selectedText.split('\n').map(line => `> ${line}`).join('\n')
                : '> Quote';
            break;
    }
    
    textarea.value = textarea.value.substring(0, start) + replacement + textarea.value.substring(end);
    textarea.focus();
    
    // Set cursor position
    const newCursorPos = start + replacement.length;
    textarea.setSelectionRange(newCursorPos, newCursorPos);
}

function enableTabSupport(textarea) {
    textarea.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = this.selectionStart;
            const end = this.selectionEnd;
            
            this.value = this.value.substring(0, start) + '    ' + this.value.substring(end);
            this.selectionStart = this.selectionEnd = start + 4;
        }
    });
}

function addLivePreview(textarea) {
    const previewBtn = document.querySelector('[data-action="preview"]');
    if (!previewBtn) return;
    
    previewBtn.addEventListener('click', function() {
        togglePreview(textarea);
    });
}

function togglePreview(textarea) {
    let preview = document.querySelector('.markdown-preview');
    
    if (preview) {
        preview.remove();
        return;
    }
    
    preview = document.createElement('div');
    preview.className = 'markdown-preview glass-card';
    preview.innerHTML = '<div class="preview-content">Loading preview...</div>';
    
    textarea.parentNode.appendChild(preview);
    
    // Convert markdown to HTML (simplified)
    const content = textarea.value;
    const htmlContent = convertMarkdownToHtml(content);
    preview.querySelector('.preview-content').innerHTML = htmlContent;
}

function convertMarkdownToHtml(markdown) {
    // Basic markdown conversion (you'd want to use a proper library in production)
    return markdown
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
        .replace(/\*(.*)\*/gim, '<em>$1</em>')
        .replace(/`([^`]+)`/gim, '<code>$1</code>')
        .replace(/\n/gim, '<br>');
}

function initializeSystemConnections() {
    const systemSelector = document.querySelector('.system-selector');
    if (!systemSelector) return;
    
    const checkboxes = systemSelector.querySelectorAll('input[type="checkbox"]');
    const counter = document.querySelector('.selection-count .count');
    
    function updateCounter() {
        const selected = Array.from(checkboxes).filter(cb => cb.checked).length;
        if (counter) counter.textContent = selected;
    }
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateCounter);
    });
    
    updateCounter();
}

function calculateReadingTime() {
    const contentField = document.querySelector('#id_content');
    const readingTimeField = document.querySelector('#id_reading_time');
    
    if (!contentField || !readingTimeField) return;
    
    function updateReadingTime() {
        const wordCount = contentField.value.split(/\s+/).filter(word => word.length > 0).length;
        const readingTime = Math.max(1, Math.ceil(wordCount / 200)); // 200 words per minute
        
        if (!readingTimeField.value || readingTimeField.dataset.autoCalculated === 'true') {
            readingTimeField.value = readingTime;
            readingTimeField.dataset.autoCalculated = 'true';
        }
    }
    
    contentField.addEventListener('input', updateReadingTime);
    readingTimeField.addEventListener('input', function() {
        this.dataset.autoCalculated = 'false';
    });
    
    updateReadingTime();
}