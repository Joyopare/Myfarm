// FarmConnect Modern JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeAnimations();
    initializeFormValidation();
    initializeCartFunctionality();
    initializeSearch();
    initializeNotifications();
    initializeImageUpload();
    initializeLazyLoading();
    initializeNavigation();
});

// Navigation and Dropdown Enhancements
function initializeNavigation() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Handle dropdown animations
    const dropdowns = document.querySelectorAll('.dropdown-toggle');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('show.bs.dropdown', function () {
            const menu = this.nextElementSibling;
            if (menu) {
                menu.style.animation = 'dropdownSlide 0.3s ease';
            }
        });
    });
    
    // Handle cart badge updates periodically
    setInterval(updateCartCount, 30000); // Update every 30 seconds
    setInterval(updateNotificationCount, 30000); // Update notifications every 30 seconds
}

function updateCartCount() {
    fetch('/orders/cart-count/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const cartBadges = document.querySelectorAll('.cart-count');
                cartBadges.forEach(badge => {
                    badge.textContent = data.count;
                    badge.style.display = data.count > 0 ? 'inline-block' : 'none';
                });
            }
        })
        .catch(error => {
            console.error('Error updating cart count:', error);
        });
}

function updateNotificationCount() {
    fetch('/messaging/notification-count/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const notificationBadges = document.querySelectorAll('.notification-badge');
                notificationBadges.forEach(badge => {
                    badge.textContent = data.count;
                    badge.style.display = data.count > 0 ? 'inline-block' : 'none';
                });
            }
        })
        .catch(error => {
            console.error('Error updating notification count:', error);
        });
}

// Animation on scroll
function initializeAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);

    // Observe all cards and sections
    document.querySelectorAll('.card, .product-card, .farmer-card').forEach(el => {
        observer.observe(el);
    });
}

// Form validation enhancement
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    showFieldError(field, 'This field is required');
                } else {
                    clearFieldError(field);
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showNotification('Please fill in all required fields', 'error');
            }
        });
        
        // Real-time validation
        form.querySelectorAll('.form-control, .form-select').forEach(field => {
            field.addEventListener('blur', function() {
                validateField(field);
            });
        });
    });
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let message = '';
    
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        message = 'This field is required';
    } else if (field.type === 'email' && value && !isValidEmail(value)) {
        isValid = false;
        message = 'Please enter a valid email address';
    } else if (field.type === 'tel' && value && !isValidPhone(value)) {
        isValid = false;
        message = 'Please enter a valid phone number';
    }
    
    if (isValid) {
        clearFieldError(field);
    } else {
        showFieldError(field, message);
    }
    
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    field.classList.add('is-invalid');
    
    const feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    feedback.textContent = message;
    field.parentNode.appendChild(feedback);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const feedback = field.parentNode.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.remove();
    }
}

// Cart functionality
function initializeCartFunctionality() {
    // Add to cart buttons
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            const quantity = this.dataset.quantity || 1;
            
            addToCart(productId, quantity);
        });
    });
    
    // Quantity controls
    document.querySelectorAll('.quantity-control').forEach(control => {
        const input = control.querySelector('input[type="number"]');
        const minusBtn = control.querySelector('.minus');
        const plusBtn = control.querySelector('.plus');
        
        if (minusBtn) {
            minusBtn.addEventListener('click', () => {
                if (input.value > 1) {
                    input.value = parseInt(input.value) - 1;
                    updateCartItem(input.dataset.itemId, input.value);
                }
            });
        }
        
        if (plusBtn) {
            plusBtn.addEventListener('click', () => {
                input.value = parseInt(input.value) + 1;
                updateCartItem(input.dataset.itemId, input.value);
            });
        }
    });
}

function addToCart(productId, quantity) {
    const button = document.querySelector(`[data-product-id="${productId}"]`);
    const originalText = button.innerHTML;
    
    button.innerHTML = '<span class="loading-spinner"></span> Adding...';
    button.disabled = true;
    
    fetch(`/orders/add-to-cart/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ quantity: quantity })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message || 'Added to cart!', 'success');
            updateCartCount(data.cart_count);
        } else {
            showNotification(data.error || 'Failed to add to cart', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred. Please try again.', 'error');
    })
    .finally(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

function updateCartItem(itemId, quantity) {
    fetch(`/orders/update-cart/${itemId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ quantity: quantity })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartTotal(data.total);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Search functionality
function initializeSearch() {
    const searchInput = document.querySelector('#search-input');
    const searchResults = document.querySelector('#search-results');
    
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length < 2) {
                searchResults.innerHTML = '';
                return;
            }
            
            searchTimeout = setTimeout(() => {
                performSearch(query);
            }, 300);
        });
    }
}

function performSearch(query) {
    fetch(`/products/search/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data.results);
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

function displaySearchResults(results) {
    const searchResults = document.querySelector('#search-results');
    
    if (results.length === 0) {
        searchResults.innerHTML = '<div class="p-3 text-muted">No products found</div>';
        return;
    }
    
    const html = results.map(product => `
        <div class="search-result-item p-3 border-bottom">
            <div class="d-flex align-items-center">
                <img src="${product.image || '/static/images/placeholder.jpg'}" 
                     alt="${product.name}" class="rounded me-3" width="50" height="50">
                <div>
                    <h6 class="mb-1">${product.name}</h6>
                    <p class="mb-0 text-muted">$${product.price}</p>
                </div>
            </div>
        </div>
    `).join('');
    
    searchResults.innerHTML = html;
}

// Notification system
function initializeNotifications() {
    // WebSocket notifications would go here
    // For now, just handle notification display
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Image upload preview
function initializeImageUpload() {
    document.querySelectorAll('input[type="file"][accept*="image"]').forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    displayImagePreview(e.target.result);
                };
                reader.readAsDataURL(file);
            }
        });
    });
}

function displayImagePreview(imageSrc) {
    let preview = document.querySelector('#image-preview');
    if (!preview) {
        preview = document.createElement('div');
        preview.id = 'image-preview';
        preview.className = 'mt-3';
        document.querySelector('input[type="file"][accept*="image"]').parentNode.appendChild(preview);
    }
    
    preview.innerHTML = `
        <img src="${imageSrc}" alt="Preview" class="img-thumbnail" style="max-width: 200px;">
        <button type="button" class="btn btn-sm btn-danger ms-2" onclick="removeImagePreview()">Remove</button>
    `;
}

function removeImagePreview() {
    const preview = document.querySelector('#image-preview');
    if (preview) {
        preview.remove();
    }
    const input = document.querySelector('input[type="file"][accept*="image"]');
    input.value = '';
}

// Lazy loading for images
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Utility functions
function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isValidPhone(phone) {
    return /^[\d\s\-\+\(\)]+$/.test(phone) && phone.replace(/\D/g, '').length >= 10;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateCartCount(count) {
    const cartBadge = document.querySelector('.cart-badge');
    if (cartBadge) {
        cartBadge.textContent = count;
        cartBadge.style.display = count > 0 ? 'inline-block' : 'none';
    }
}

function updateCartTotal(total) {
    const totalElement = document.querySelector('#cart-total');
    if (totalElement) {
        totalElement.textContent = `$${total.toFixed(2)}`;
    }
}

// Follow/Unfollow functionality
function toggleFollow(farmerId, button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="loading-spinner"></span>';
    button.disabled = true;
    
    fetch(`/accounts/follow-farmer/${farmerId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            button.innerHTML = data.following ? 'Following' : 'Follow';
            button.className = data.following ? 'btn btn-secondary' : 'btn btn-primary';
            
            // Update followers count
            const countElement = document.querySelector(`#followers-count-${farmerId}`);
            if (countElement) {
                countElement.textContent = data.followers_count;
            }
            
            showNotification(data.message, 'success');
        } else {
            showNotification(data.error || 'Failed to update follow status', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred. Please try again.', 'error');
    })
    .finally(() => {
        button.disabled = false;
    });
}

// Rating functionality
function submitRating(farmerId) {
    const rating = document.querySelector(`#rating-${farmerId}`).value;
    const review = document.querySelector(`#review-${farmerId}`).value;
    
    if (!rating) {
        showNotification('Please select a rating', 'error');
        return;
    }
    
    fetch(`/accounts/rate-farmer/${farmerId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: `rating=${rating}&review=${encodeURIComponent(review)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Rating submitted successfully!', 'success');
            // Update rating display
            location.reload();
        } else {
            showNotification(data.error || 'Failed to submit rating', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred. Please try again.', 'error');
    });
}
