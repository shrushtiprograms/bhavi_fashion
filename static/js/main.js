// Main JavaScript for Bhavi India Fashion

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Product quantity selector
    const quantityBtns = document.querySelectorAll('.quantity-btn');
    quantityBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.closest('.quantity-selector').querySelector('.quantity-input');
            const currentValue = parseInt(input.value);
            
            if (this.classList.contains('quantity-decrease')) {
                if (currentValue > 1) {
                    input.value = currentValue - 1;
                }
            } else {
                input.value = currentValue + 1;
            }
            
            // Trigger change event for any listeners
            const event = new Event('change');
            input.dispatchEvent(event);
        });
    });

    // Add to cart functionality
    // const addToCartBtns = document.querySelectorAll('.add-to-cart-btn');
    // addToCartBtns.forEach(btn => {
    //     btn.addEventListener('click', function(e) {
    //         e.preventDefault();
            
    //         const productId = this.dataset.productId;
    //         const quantity = this.closest('.product-actions')?.querySelector('.quantity-input')?.value || 1;
            
    //         // Show loading
    //         this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Adding...';
    //         this.disabled = true;
            
    //         // In a real application, you would make an AJAX request to add the product to the cart
    //         // For demo purposes, we'll just simulate a delay and success
    //         setTimeout(() => {
    //             this.innerHTML = 'Added to Cart';
                
    //             // Update cart count
    //             const cartCount = document.querySelector('.cart-count');
    //             if (cartCount) {
    //                 cartCount.textContent = parseInt(cartCount.textContent) + parseInt(quantity);
    //             }
                
    //             // Reset button after a delay
    //             setTimeout(() => {
    //                 this.innerHTML = 'Add to Cart';
    //                 this.disabled = false;
    //             }, 2000);
                
    //             // Show toast notification
    //             const toastContainer = document.getElementById('toast-container');
    //             if (toastContainer) {
    //                 const toast = document.createElement('div');
    //                 toast.classList.add('toast', 'show');
    //                 toast.setAttribute('role', 'alert');
    //                 toast.setAttribute('aria-live', 'assertive');
    //                 toast.setAttribute('aria-atomic', 'true');
                    
    //                 toast.innerHTML = `
    //                     <div class="toast-header">
    //                         <strong class="me-auto">Success</strong>
    //                         <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
    //                     </div>
    //                     <div class="toast-body">
    //                         Product added to your cart.
    //                     </div>
    //                 `;
                    
    //                 toastContainer.appendChild(toast);
                    
    //                 setTimeout(() => {
    //                     toast.classList.remove('show');
    //                     setTimeout(() => {
    //                         toastContainer.removeChild(toast);
    //                     }, 500);
    //                 }, 3000);
    //             }
    //         }, 1000);
    //     });
    //});

    // Add to wishlist functionality
    const wishlistBtns = document.querySelectorAll('.wishlist-btn');
    wishlistBtns.forEach(btn => {
        const productId = btn.dataset.productId;
        if (!productId || productId === 'undefined') {
            console.error('Invalid product ID:', productId);
            return;
        }

        const icon = btn.querySelector('i.fa-heart');
        let isInWishlist = btn.dataset.inWishlist === 'true';
        if (icon && isInWishlist) {
            icon.classList.remove('far');
            icon.classList.add('fas', 'text-danger');
        }

        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const url = isInWishlist ? `/products/wishlist/remove/${productId}/` : `/products/wishlist/add/${productId}/`;

            fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    isInWishlist = !isInWishlist; // Toggle state
                    if (isInWishlist) {
                        icon.classList.remove('far');
                        icon.classList.add('fas', 'text-danger');
                        btn.dataset.inWishlist = 'true';
                        showNotification(`${data.message || 'Added to wishlist'}`, 'success');
                    } else {
                        icon.classList.remove('fas', 'text-danger');
                        icon.classList.add('far');
                        btn.dataset.inWishlist = 'false';
                        showNotification(`${data.message || 'Removed from wishlist'}`, 'success');
                    }
                } else {
                    console.error(data.message);
                    showNotification(data.message || 'Error updating wishlist', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Login to add to Wishlist', 'warning');
            });
        });
    });

    
    const priceSlider = document.getElementById('price-range');
    const maxPrice = document.getElementById('max-price');
    if (priceSlider && maxPrice) {
        priceSlider.addEventListener('input', function() {
            maxPrice.textContent = this.value >= 10000 ? '₹10,000+' : '₹' + this.value;
        });
        priceSlider.addEventListener('change', function() {
            document.getElementById('filter-form').submit();
        });
    }

    // Auto-submit filter form on change
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        const inputs = filterForm.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                filterForm.submit();
            });
        });
    }

    // Auto-submit sort form
    const sortSelect = document.getElementById('sort');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            document.getElementById('sort-form').submit();
        });
    }

    // Filter toggle on mobile
    const filterToggle = document.getElementById('filter-toggle');
    if (filterToggle) {
        filterToggle.addEventListener('click', function() {
            const filterContent = document.getElementById('filter-content');
            if (filterContent) {
                filterContent.classList.toggle('show');
                this.innerHTML = filterContent.classList.contains('show') ? 'Hide Filters' : 'Show Filters';
            }
        });
    }

    // Image zoom on product detail page (simple version)
    const productMainImage = document.getElementById('product-main-image');
    if (productMainImage) {
        productMainImage.addEventListener('mousemove', function(e) {
            const { left, top, width, height } = this.getBoundingClientRect();
            const x = (e.clientX - left) / width;
            const y = (e.clientY - top) / height;
            
            this.style.transformOrigin = `${x * 100}% ${y * 100}%`;
        });
        
        productMainImage.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.5)';
        });
        
        productMainImage.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.transformOrigin = 'center center';
        });
    }

    // Thumbnail gallery on product detail page
    const productThumbnails = document.querySelectorAll('.product-thumbnail');
    productThumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            // Remove active class from all thumbnails
            productThumbnails.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked thumbnail
            this.classList.add('active');
            
            // Update main image
            const mainImage = document.getElementById('product-main-image');
            if (mainImage) {
                mainImage.src = this.dataset.image;
            }
        });
    });
});
function showNotification(message, type) {
    const alertClass = type === 'success' ? 'alert-success' :
                      type === 'danger' ? 'alert-danger' :
                      type === 'warning' ? 'alert-warning' : 'alert-info';

    const notification = $(`
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);

    $('#notification-area').append(notification);
    setTimeout(() => {
        notification.alert('close');
    }, 3000);
}