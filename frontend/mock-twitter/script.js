// Mock Twitter App - JavaScript Functionality
class MockTwitterApp {
    constructor() {
        this.posts = [];
        this.currentImageFile = null;
        this.initializeApp();
    }

    initializeApp() {
        this.bindEventListeners();
        this.setupTextareaAutoResize();
        this.loadSamplePosts();
    }

    bindEventListeners() {
        // Post composer events
        const postText = document.getElementById('post-text');
        const imageUpload = document.getElementById('image-upload');
        const removeImage = document.getElementById('remove-image');
        const postBtn = document.getElementById('post-btn');
        const locationSelect = document.getElementById('location-select');

        // Text input events
        postText.addEventListener('input', () => this.handleTextInput());
        postText.addEventListener('focus', () => this.handleTextFocus());
        postText.addEventListener('blur', () => this.handleTextBlur());

        // Image upload events
        imageUpload.addEventListener('change', (e) => this.handleImageUpload(e));
        removeImage.addEventListener('click', () => this.removeImage());

        // Post submission
        postBtn.addEventListener('click', () => this.submitPost());

        // Enter key handling (Ctrl/Cmd + Enter to post)
        postText.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                this.submitPost();
            }
        });

        // Modal events
        const imageModal = document.getElementById('image-modal');
        const modalClose = document.querySelector('.modal-close');
        const modalBackdrop = document.querySelector('.modal-backdrop');

        modalClose.addEventListener('click', () => this.closeImageModal());
        modalBackdrop.addEventListener('click', () => this.closeImageModal());

        // ESC key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeImageModal();
            }
        });
    }

    setupTextareaAutoResize() {
        const textarea = document.getElementById('post-text');
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 200) + 'px';
        });
    }

    handleTextInput() {
        const postText = document.getElementById('post-text');
        const charCounter = document.getElementById('char-counter');
        const postBtn = document.getElementById('post-btn');
        
        const remaining = 280 - postText.value.length;
        charCounter.textContent = remaining;
        
        // Update character counter styling
        charCounter.className = 'char-counter';
        if (remaining < 20) {
            charCounter.classList.add('warning');
        }
        if (remaining < 0) {
            charCounter.classList.add('danger');
        }
        
        // Enable/disable post button
        const hasContent = postText.value.trim().length > 0 || this.currentImageFile;
        const withinLimit = remaining >= 0;
        postBtn.disabled = !hasContent || !withinLimit;
    }

    handleTextFocus() {
        const composer = document.querySelector('.composer-section');
        composer.style.boxShadow = '0 4px 16px rgba(29, 161, 242, 0.2)';
    }

    handleTextBlur() {
        const composer = document.querySelector('.composer-section');
        composer.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
    }

    handleImageUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Validate file type
        if (!file.type.startsWith('image/')) {
            this.showToast('Please select a valid image file.', 'error');
            return;
        }

        // Validate file size (5MB limit)
        if (file.size > 5 * 1024 * 1024) {
            this.showToast('Image size must be less than 5MB.', 'error');
            return;
        }

        this.currentImageFile = file;
        this.displayImagePreview(file);
        this.handleTextInput(); // Update post button state
    }

    displayImagePreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const imagePreview = document.getElementById('image-preview');
            const previewImg = document.getElementById('preview-img');
            
            previewImg.src = e.target.result;
            imagePreview.classList.remove('hidden');
            
            // Add fade-in animation
            imagePreview.style.opacity = '0';
            setTimeout(() => {
                imagePreview.style.transition = 'opacity 0.3s ease';
                imagePreview.style.opacity = '1';
            }, 10);
        };
        reader.readAsDataURL(file);
    }

    removeImage() {
        this.currentImageFile = null;
        const imagePreview = document.getElementById('image-preview');
        const imageUpload = document.getElementById('image-upload');
        
        imagePreview.classList.add('hidden');
        imageUpload.value = '';
        this.handleTextInput(); // Update post button state
    }

    async submitPost() {
        const postText = document.getElementById('post-text');
        const locationSelect = document.getElementById('location-select');
        const postBtn = document.getElementById('post-btn');
        
        const text = postText.value.trim();
        const location = locationSelect.value;
        
        if (!text && !this.currentImageFile) {
            this.showToast('Please enter some text or add an image.', 'error');
            return;
        }

        // Show loading state
        this.showLoadingOverlay();
        postBtn.classList.add('loading');
        postBtn.disabled = true;

        try {
            // Create post object for display (keeping location separate)
            const post = {
                image: null,
                timestamp: new Date().toISOString(),
                text: text,
                location: location || null
            };
            
            // Create server post object (combining text and location)
            let combinedText = text;
            if (location) {
                combinedText = text + ' ' + location;
            }
            const serverPost = {
                image: null,
                timestamp: post.timestamp,
                text: combinedText
            };
            // Handle image if present
            if (this.currentImageFile) {
                const imageBase64 = await this.convertImageToBase64(this.currentImageFile);
                post.image = imageBase64;
                serverPost.image = imageBase64;
            }
            // Save post to database (with combined text+location)
            await fetch('http://localhost:8000/save-post', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(serverPost)
            });
            
            // Refresh posts from database to show the new post
            await this.loadPostsFromServer();
            
            // Reset form
            this.resetComposer();
            // Show success message
            this.showToast('Post shared successfully!', 'success');
        } catch (error) {
            console.error('Error submitting post:', error);
            this.showToast('Failed to post. Please try again.', 'error');
        } finally {
            this.hideLoadingOverlay();
            postBtn.classList.remove('loading');
            this.handleTextInput(); // Reset button state
        }
    }

    convertImageToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    resetComposer() {
        document.getElementById('post-text').value = '';
        document.getElementById('location-select').value = '';
        document.getElementById('post-text').style.height = 'auto';
        this.removeImage();
    }

    addPostToFeed(post) {
        this.posts.unshift(post); // Add to beginning of array
        this.renderPost(post, true); // true for new post animation
    }

    renderPost(post, isNew = false) {
        const postsFeed = document.getElementById('posts-feed');
        const postElement = this.createPostElement(post);
        
        if (isNew) {
            // Add new post to top with animation
            postElement.style.transform = 'translateY(-20px)';
            postElement.style.opacity = '0';
            postsFeed.insertBefore(postElement, postsFeed.firstChild);
            
            // Trigger animation
            setTimeout(() => {
                postElement.style.transition = 'all 0.5s ease-out';
                postElement.style.transform = 'translateY(0)';
                postElement.style.opacity = '1';
            }, 10);
        } else {
            postsFeed.appendChild(postElement);
        }
    }

    createPostElement(post) {
        const postDiv = document.createElement('div');
        postDiv.className = 'post';
        // Use default avatar and username for all posts
        const defaultAvatar = '👤';
        const defaultUsername = 'Emergency User';
        const defaultHandle = '@emergency_user';
        postDiv.innerHTML = `
            <div class="post-header">
                <div class="avatar">${defaultAvatar}</div>
                <div class="post-meta">
                    <span class="post-username">${defaultUsername}</span>
                    <span class="post-handle">${defaultHandle}</span>
                    <span class="post-time">• ${this.formatTimestamp(post.timestamp)}</span>
                </div>
            </div>
            <div class="post-content">
                ${post.text ? `<div class="post-text">${this.formatPostText(post.text)}</div>` : ''}
                ${post.image ? `
                    <div class="post-image" onclick="app.openImageModal('${post.image}')">
                        <img src="${post.image}" alt="Post image" loading="lazy">
                    </div>
                ` : ''}
                ${post.location ? `
                    <div class="post-location">
                        📍 ${post.location}
                    </div>
                ` : ''}
            </div>
        `;
        return postDiv;
    }

    formatPostText(text) {
        // Basic text formatting (links, hashtags, mentions)
        return text
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>')
            .replace(/#(\w+)/g, '<span style="color: #1da1f2; font-weight: 500;">#$1</span>')
            .replace(/@(\w+)/g, '<span style="color: #1da1f2; font-weight: 500;">@$1</span>');
    }

    formatTimestamp(timestamp) {
        const now = new Date();
        const postTime = new Date(timestamp);
        const diffMs = now - postTime;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'now';
        if (diffMins < 60) return `${diffMins}m`;
        if (diffHours < 24) return `${diffHours}h`;
        if (diffDays < 7) return `${diffDays}d`;
        return postTime.toLocaleDateString();
    }

    openImageModal(imageSrc) {
        const modal = document.getElementById('image-modal');
        const modalImage = document.getElementById('modal-image');
        
        modalImage.src = imageSrc;
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }

    closeImageModal() {
        const modal = document.getElementById('image-modal');
        modal.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }

    showLoadingOverlay() {
        document.getElementById('loading-overlay').classList.remove('hidden');
    }

    hideLoadingOverlay() {
        document.getElementById('loading-overlay').classList.add('hidden');
    }

    showToast(message, type = 'success') {
        const toastId = type === 'success' ? 'success-toast' : 'error-toast';
        const toast = document.getElementById(toastId);
        const messageEl = toast.querySelector('.toast-message');
        
        messageEl.textContent = message;
        toast.classList.remove('hidden');
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 3000);
    }

    loadSamplePosts() {
        // Load posts from server (database) instead of hardcoded samples
        this.loadPostsFromServer();
    }

    async loadPostsFromServer() {
        try {
            console.log('📡 Fetching posts from server...');
            
            const response = await fetch('http://localhost:8000/get-posts');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (result.status === 'success') {
                console.log(`✅ Loaded ${result.total_count} posts from ${result.source}`);
                
                // Clear existing posts
                this.posts = [];
                const postsFeed = document.getElementById('posts-feed');
                postsFeed.innerHTML = '';
                
                // Add each post from the database to the feed
                if (result.posts && result.posts.length > 0) {
                    result.posts.forEach(post => {
                        // Parse location from text if it was stored combined
                        const { text, location } = this.parseTextAndLocation(post.text);
                        
                        const displayPost = {
                            text: text,
                            image: post.image,
                            location: location,
                            timestamp: post.timestamp
                        };
                        
                        this.posts.push(displayPost);
                        this.renderPost(displayPost);
                    });
                } else {
                    console.log('📭 No posts found in database');
                    // Show a message when no posts exist
                    this.showNoPosts();
                }
            } else {
                throw new Error(result.message || 'Failed to load posts');
            }
            
        } catch (error) {
            console.error('❌ Failed to load posts from server:', error);
            // Fall back to showing a message about the issue
            this.showLoadError();
        }
    }

    parseTextAndLocation(combinedText) {
        // Try to extract location from combined text
        // Look for common location patterns at the end
        const locationPatterns = [
            /\s+(San Jose, CA|San Francisco, CA|Palo Alto, CA|Oakland, CA|Berkeley, CA)$/i
        ];
        
        for (const pattern of locationPatterns) {
            const match = combinedText.match(pattern);
            if (match) {
                const location = match[1];
                const text = combinedText.replace(pattern, '').trim();
                return { text, location };
            }
        }
        
        // If no location pattern found, return original text
        return { text: combinedText, location: null };
    }

    showNoPosts() {
        const postsFeed = document.getElementById('posts-feed');
        postsFeed.innerHTML = `
            <div class="no-posts-message" style="padding: 40px 20px; text-align: center; color: #657786;">
                <div style="font-size: 48px; margin-bottom: 16px;">📭</div>
                <h3 style="margin-bottom: 8px; color: #14171a;">No posts yet</h3>
                <p>Be the first to report emergency information!</p>
            </div>
        `;
    }

    showLoadError() {
        const postsFeed = document.getElementById('posts-feed');
        postsFeed.innerHTML = `
            <div class="error-message" style="padding: 40px 20px; text-align: center; color: #e0245e;">
                <div style="font-size: 48px; margin-bottom: 16px;">⚠️</div>
                <h3 style="margin-bottom: 8px;">Failed to load posts</h3>
                <p style="color: #657786;">Please check if the server is running and try refreshing the page.</p>
                <button onclick="app.loadPostsFromServer()" style="margin-top: 16px; padding: 8px 16px; background: #1da1f2; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    Try Again
                </button>
            </div>
        `;
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new MockTwitterApp();
});

// Export for global access
window.MockTwitterApp = MockTwitterApp;