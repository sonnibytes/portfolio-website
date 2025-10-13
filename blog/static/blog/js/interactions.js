// blog/static/blog/js/interactions.js
// Handles Share, Bookmark, and Subscribe functionality

/**
 * SHARE FUNCTIONALITY
 * Uses Web Share API (mobile-friendly) with fallback to copy link
 */

// Copy link to clipboard
function copyToClipboard(text) {
    // Modern approach using Clipboard API
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Link copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Failed to copy:', err);
            fallbackCopy(text);
        });
    } else {
        // Fallback for older browsers
        fallbackCopy(text);
    }
}

// Fallback copy method for older browsers
function fallbackCopy(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showNotification('Link copied to clipboard!', 'success');
    } catch (err) {
        console.error('Fallback copy failed:', err);
        showNotification('Failed to copy link', 'error');
    }
    
    document.body.removeChild(textArea);
}

// Enhanced share function using Web Share API
function sharePost(title, text, url) {
    // Check if Web Share API is available (mostly mobile devices)
    if (navigator.share) {
        navigator.share({
            title: title,
            text: text,
            url: url
        })
        .then(() => console.log('Shared successfully'))
        .catch((error) => console.log('Error sharing:', error));
    } else {
        // Fallback: just copy the link
        copyToClipboard(url);
    }
}

// Initialize share buttons
function initShareButtons() {
    // Handle all share buttons
    document.querySelectorAll('[data-share-url]').forEach(button => {
        button.addEventListener('click', function() {
            const url = this.dataset.shareUrl;
            const title = this.dataset.shareTitle || 'Check out this post';
            const text = this.dataset.shareText || '';
            
            sharePost(title, text, url);
        });
    });
}


/**
 * BOOKMARK FUNCTIONALITY
 * Uses localStorage to store bookmarked post IDs (no server needed)
 */

// Key for localStorage
const BOOKMARKS_KEY = 'aura_bookmarks';

// Get all bookmarked post IDs
function getBookmarks() {
    const bookmarks = localStorage.getItem(BOOKMARKS_KEY);
    return bookmarks ? JSON.parse(bookmarks) : [];
}

// Save bookmarks to localStorage
function saveBookmarks(bookmarks) {
    localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(bookmarks));
}

// Check if a post is bookmarked
function isBookmarked(postId) {
    const bookmarks = getBookmarks();
    return bookmarks.includes(postId);
}

// Add a bookmark
function addBookmark(postId) {
    const bookmarks = getBookmarks();
    
    if (!bookmarks.includes(postId)) {
        bookmarks.push(postId);
        saveBookmarks(bookmarks);
        return true;
    }
    
    return false;
}

// Remove a bookmark
function removeBookmark(postId) {
    let bookmarks = getBookmarks();
    const initialLength = bookmarks.length;
    
    bookmarks = bookmarks.filter(id => id !== postId);
    saveBookmarks(bookmarks);
    
    return bookmarks.length < initialLength;
}

// Toggle bookmark status
function toggleBookmark(postId) {
    if (isBookmarked(postId)) {
        removeBookmark(postId);
        return false; // Now not bookmarked
    } else {
        addBookmark(postId);
        return true; // Now bookmarked
    }
}

// Update bookmark button appearance
function updateBookmarkButton(button, isBookmarked) {
    const icon = button.querySelector('i');
    
    if (isBookmarked) {
        // Bookmarked state - solid icon
        icon.classList.remove('fa-bookmark');
        icon.classList.add('fa-bookmark', 'fas');
        button.classList.add('bookmarked');
        button.setAttribute('title', 'Remove bookmark');
    } else {
        // Not bookmarked - outline icon
        icon.classList.remove('fas');
        icon.classList.add('fa-bookmark', 'far');
        button.classList.remove('bookmarked');
        button.setAttribute('title', 'Bookmark');
    }
}

// Initialize bookmark buttons
function initBookmarkButtons() {
    document.querySelectorAll('[data-bookmark-id]').forEach(button => {
        const postId = parseInt(button.dataset.bookmarkId);
        
        // Set initial state
        updateBookmarkButton(button, isBookmarked(postId));
        
        // Add click handler
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const nowBookmarked = toggleBookmark(postId);
            updateBookmarkButton(button, nowBookmarked);
            
            // Show notification
            if (nowBookmarked) {
                showNotification('Post bookmarked!', 'success');
            } else {
                showNotification('Bookmark removed', 'info');
            }
            
            // Dispatch custom event for other parts of the page to listen to
            window.dispatchEvent(new CustomEvent('bookmarkChanged', {
                detail: { postId, isBookmarked: nowBookmarked }
            }));
        });
    });
}

// Get count of bookmarks
function getBookmarkCount() {
    return getBookmarks().length;
}


/**
 * SUBSCRIBE FUNCTIONALITY
 * Collects email addresses and saves to database via AJAX
 */

// Handle subscription form submission
function handleSubscribeForm(form) {
    const emailInput = form.querySelector('input[name="email"]');
    const submitButton = form.querySelector('button[type="submit"]');
    const email = emailInput.value.trim();
    
    // Validate email
    if (!email || !isValidEmail(email)) {
        showNotification('Please enter a valid email address', 'error');
        return;
    }
    
    // Get subscription scope and context
    const scopeInput = form.querySelector('input[name="subscribe_scope"]:checked');
    const scope = scopeInput ? scopeInput.value : 'all';
    
    // Build form data
    const formData = new URLSearchParams();
    formData.append('email', email);
    formData.append('scope', scope);
    
    // Add context-specific data
    if (scope === 'category') {
        const categoryId = scopeInput.dataset.categoryId;
        if (categoryId) formData.append('category_id', categoryId);
    } else if (scope === 'tag') {
        const tagId = scopeInput.dataset.tagId;
        if (tagId) formData.append('tag_id', tagId);
    } else if (scope === 'series') {
        const seriesId = scopeInput.dataset.seriesId;
        if (seriesId) formData.append('series_id', seriesId);
    }
    
    // Disable button to prevent double submission
    submitButton.disabled = true;
    const originalHTML = submitButton.innerHTML;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Subscribing...';
    
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Send AJAX request
    fetch('/datalogs/subscribe/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: formData.toString()
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            emailInput.value = ''; // Clear input
            
            // Store in localStorage for "already subscribed" check
            const subscriptionInfo = {
                email: email,
                scope: scope,
                subscribedAt: new Date().toISOString()
            };
            localStorage.setItem('aura_subscribed_email', JSON.stringify(subscriptionInfo));
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Subscription error:', error);
        showNotification('An error occurred. Please try again.', 'error');
    })
    .finally(() => {
        // Re-enable button
        submitButton.disabled = false;
        submitButton.innerHTML = originalHTML;
    });
}

// Validate email format
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Initialize subscribe forms
function initSubscribeForms() {
    document.querySelectorAll('.subscribe-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            handleSubscribeForm(this);
        });
    });
    
    // Check if user already subscribed and show message
    const subscribedEmail = localStorage.getItem('aura_subscribed_email');
    if (subscribedEmail) {
        document.querySelectorAll('.subscribe-status').forEach(el => {
            el.textContent = `Subscribed as ${subscribedEmail}`;
            el.style.display = 'block';
        });
    }
}


/**
 * NOTIFICATION SYSTEM
 * Shows toast notifications for user feedback
 */

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span class="notification-icon">
            ${getNotificationIcon(type)}
        </span>
        <span class="notification-message">${message}</span>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Trigger animation
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function getNotificationIcon(type) {
    const icons = {
        'success': '<i class="fas fa-check-circle"></i>',
        'error': '<i class="fas fa-exclamation-circle"></i>',
        'info': '<i class="fas fa-info-circle"></i>',
        'warning': '<i class="fas fa-exclamation-triangle"></i>'
    };
    return icons[type] || icons.info;
}


/**
 * INITIALIZE ALL INTERACTIONS
 * Call this when page loads
 */

function initInteractions() {
    initShareButtons();
    initBookmarkButtons();
    initSubscribeForms();
    
    console.log('✓ DataLog interactions initialized');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initInteractions);
} else {
    initInteractions();
}


/**
 * EXPORT FUNCTIONS FOR USE IN OTHER FILES
 */

// Make functions available globally
window.AURAInteractions = {
    // Share
    sharePost,
    copyToClipboard,
    
    // Bookmarks
    getBookmarks,
    isBookmarked,
    addBookmark,
    removeBookmark,
    toggleBookmark,
    getBookmarkCount,
    
    // Subscribe
    handleSubscribeForm,
    
    // Notifications
    showNotification,
    
    // Init
    init: initInteractions
};