// Mock Twitter App - JavaScript Functionality
class MockTwitterApp {
    constructor() {
        this.posts = [];
        this.currentImageFile = null;
        this.initializeApp();
        this.loadSamplePosts();
    }

    initializeApp() {
        this.bindEventListeners();
        this.setupTextareaAutoResize();
        this.loadPostsFromStorage();
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
            // Create post object
            const post = {
                id: `post_${Date.now()}`,
                text: text,
                image: null,
                location: location,
                timestamp: new Date().toISOString(),
                user: {
                    username: 'Emergency User',
                    handle: '@emergency_user',
                    avatar: '👤'
                }
            };

            // Handle image if present
            if (this.currentImageFile) {
                post.image = await this.convertImageToBase64(this.currentImageFile);
            }

            // Simulate API call delay
            await this.delay(1500);

            // Add post to feed
            this.addPostToFeed(post);
            this.savePostsToStorage();

            // Save post to JSON file in frontend directory
            await this.savePostToJSON(post);

            // Reset form
            this.resetComposer();
            
            // Show success message
            this.showToast('Post shared successfully! JSON file generated.', 'success');

            // Simulate sending to backend (for demo)
            this.sendToBackend(post);

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
        postDiv.innerHTML = `
            <div class="post-header">
                <div class="avatar">${post.user.avatar}</div>
                <div class="post-meta">
                    <span class="post-username">${post.user.username}</span>
                    <span class="post-handle">${post.user.handle}</span>
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

    async sendToBackend(post) {
        // Simulate sending to backend API
        try {
            console.log('Sending post to backend:', post);
            
            // This would be your actual API call
            // const response = await fetch('/api/v1/twitter/process-post', {
            //     method: 'POST',
            //     headers: {
            //         'Content-Type': 'application/json',
            //     },
            //     body: JSON.stringify(post)
            // });
            
            // For demo purposes, just log
            console.log('Post sent to backend successfully');
            
        } catch (error) {
            console.error('Failed to send to backend:', error);
        }
    }

    loadSamplePosts() {
        const samplePosts = [
            {
                id: 'sample_1',
                text: '🚨 URGENT: Major earthquake felt in downtown San Jose! Buildings shaking, people evacuating. Stay safe everyone! #earthquake #SanJose',
                image: null,
                location: 'San Jose, CA',
                timestamp: new Date(Date.now() - 300000).toISOString(), // 5 minutes ago
                user: {
                    username: 'SF Emergency',
                    handle: '@sf_emergency',
                    avatar: '🚨'
                }
            },
            {
                id: 'sample_2',
                text: 'Wildfire spotted near Highway 101. Smoke visible from miles away. Authorities are responding. #wildfire #emergency',
                image: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgZmlsbD0iI0ZGNkIzNSIvPjx0ZXh0IHg9IjIwMCIgeT0iMTUwIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMjAiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+V2lsZGZpcmUgSW1hZ2U8L3RleHQ+PC9zdmc+',
                location: 'Palo Alto, CA',
                timestamp: new Date(Date.now() - 600000).toISOString(), // 10 minutes ago
                user: {
                    username: 'Fire Watch',
                    handle: '@fire_watch',
                    avatar: '🔥'
                }
            },
            {
                id: 'sample_3',
                text: 'Flooding reported on Market Street. Water levels rising rapidly. Avoid the area if possible. Emergency services on scene.',
                image: null,
                location: 'San Francisco, CA',
                timestamp: new Date(Date.now() - 900000).toISOString(), // 15 minutes ago
                user: {
                    username: 'Weather Alert',
                    handle: '@weather_alert',
                    avatar: '🌊'
                }
            }
        ];

        // Add sample posts to feed
        samplePosts.forEach(post => {
            this.posts.push(post);
            this.renderPost(post);
        });
    }

    savePostsToStorage() {
        try {
            localStorage.setItem('mockTwitterPosts', JSON.stringify(this.posts.slice(0, 50))); // Keep last 50 posts
        } catch (error) {
            console.error('Failed to save posts to storage:', error);
        }
    }

    loadPostsFromStorage() {
        try {
            const savedPosts = localStorage.getItem('mockTwitterPosts');
            if (savedPosts) {
                const posts = JSON.parse(savedPosts);
                // Only load user posts (not sample posts)
                const userPosts = posts.filter(post => post.user.handle === '@emergency_user');
                userPosts.forEach(post => {
                    this.posts.unshift(post);
                    this.renderPost(post, false);
                });
            }
        } catch (error) {
            console.error('Failed to load posts from storage:', error);
        }
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async savePostToJSON(post) {
        // Create a clean JSON object with the required fields: user, photo, location, text
        const postData = {
            post_id: post.id,
            user: {
                username: post.user.username,
                handle: post.user.handle,
                avatar: post.user.avatar
            },
            text: post.text || '',
            photo: post.image || null,
            location: post.location || '',
            metadata: {
                timestamp: post.timestamp,
                created_at: new Date(post.timestamp).toLocaleString(),
                export_timestamp: new Date().toISOString()
            }
        };

        // Send to backend to save to JSON file
        try {
            const response = await fetch('/api/v1/save-post-json', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(postData)
            });

            if (response.ok) {
                console.log('Post saved to JSON file successfully');
            } else {
                console.error('Failed to save post to JSON file');
                // Fallback: save to localStorage for now
                this.saveToLocalStorage(postData);
            }
        } catch (error) {
            console.error('Error saving post to JSON file:', error);
            // Fallback: save to localStorage
            this.saveToLocalStorage(postData);
        }
    }

    saveToLocalStorage(postData) {
        // Fallback method to save posts locally
        let savedPosts = [];
        try {
            const existingData = localStorage.getItem('twitterPostsJSON');
            if (existingData) {
                savedPosts = JSON.parse(existingData);
            }
        } catch (error) {
            console.error('Error reading localStorage:', error);
        }

        savedPosts.push(postData);
        
        // Keep only last 100 posts to prevent localStorage from getting too large
        if (savedPosts.length > 100) {
            savedPosts = savedPosts.slice(-100);
        }

        localStorage.setItem('twitterPostsJSON', JSON.stringify(savedPosts, null, 2));
        console.log('Post saved to localStorage as fallback');
    }


}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new MockTwitterApp();
});

// Export for global access
window.MockTwitterApp = MockTwitterApp;