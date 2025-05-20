/**
 * Bhavi India Fashion - Cart functionality
 * 
 * This file handles cart operations like adding, updating and removing items
 */

document.addEventListener('DOMContentLoaded', function() {
    initCartQuantityUpdates();
    initCartItemRemoval();
    initCartTotal();
    initAddressSelection();
    initPaymentMethodSelection();
});
// document.querySelector('.add-to-cart-btn').addEventListener('click', function(e) {
//     e.preventDefault();
//     fetch(`/orders/add-to-cart/${productId}/`, {
//         method: 'POST',
//         headers: {
//             'X-CSRFToken': getCsrfToken(),
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ quantity: 1 })
//     })
//     .then(response => response.json())
//     .then(data => console.log(data));
// });
/**
 * Update cart item quantities
 */
function initCartQuantityUpdates() {
    const updateForms = document.querySelectorAll('.cart-item-update-form');
    
    if (updateForms.length > 0) {
        updateForms.forEach(form => {
            const quantityInput = form.querySelector('.quantity-input');
            const updateButton = form.querySelector('.update-cart-btn');
            
            if (quantityInput && updateButton) {
                // Save initial value to detect changes
                const initialValue = quantityInput.value;
                
                // Show update button when quantity changes
                quantityInput.addEventListener('change', function() {
                    if (this.value !== initialValue) {
                        updateButton.style.display = 'inline-block';
                    } else {
                        updateButton.style.display = 'none';
                    }
                });
                
                // Handle form submission with AJAX
                form.addEventListener('submit', function(e) {
                    e.preventDefault();
                    
                    const formData = new FormData(this);
                    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                    const itemId = this.dataset.itemId;
                    
                    fetch(`/orders/update-cart-item/${itemId}/`, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': csrfToken
                        }
                    })
                    .then(response => {
                        if (response.ok) {
                            // Reload the page to show updated cart
                            window.location.reload();
                        } else {
                            throw new Error('Failed to update cart');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showAlert('Error updating cart item', 'error');
                    });
                });
            }
        });
    }
}

/**
 * Remove items from cart
 */
function initCartItemRemoval() {
    const removeButtons = document.querySelectorAll('.remove-cart-item');
    
    if (removeButtons.length > 0) {
        removeButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                if (confirm('Are you sure you want to remove this item from your cart?')) {
                    const itemId = this.dataset.itemId;
                    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                    
                    fetch(`/orders/remove-from-cart/${itemId}/`, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': csrfToken
                        }
                    })
                    .then(response => {
                        if (response.ok) {
                            // Remove the item from DOM
                            const cartItem = this.closest('.cart-item');
                            cartItem.style.animation = 'fadeOut 0.3s ease forwards';
                            
                            setTimeout(() => {
                                cartItem.remove();
                                
                                // Update cart totals
                                updateCartTotals();
                                
                                // If cart is empty, show empty message
                                if (document.querySelectorAll('.cart-item').length === 0) {
                                    const cartContainer = document.querySelector('.cart-items-container');
                                    const emptyCart = document.createElement('div');
                                    emptyCart.className = 'empty-cart text-center py-5';
                                    emptyCart.innerHTML = `
                                        <i class="fa fa-shopping-cart fa-4x text-muted mb-3"></i>
                                        <h3>Your cart is empty</h3>
                                        <p class="mb-4">Looks like you haven't added any items to your cart yet.</p>
                                        <a href="/products/" class="btn btn-primary">Continue Shopping</a>
                                    `;
                                    cartContainer.appendChild(emptyCart);
                                }
                            }, 300);
                        } else {
                            throw new Error('Failed to remove item');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showAlert('Error removing item from cart', 'error');
                    });
                }
            });
        });
    }
}

/**
 * Update cart totals based on item changes
 */
function updateCartTotals() {
    // Calculate subtotal from visible cart items
    let subtotal = 0;
    const cartItems = document.querySelectorAll('.cart-item:not([style*="animation"])');
    
    cartItems.forEach(item => {
        const price = parseFloat(item.dataset.price);
        const quantity = parseInt(item.querySelector('.quantity-input').value);
        subtotal += price * quantity;
    });
    
    // Update DOM elements
    const subtotalEl = document.querySelector('.cart-subtotal-value');
    const shippingEl = document.querySelector('.cart-shipping-value');
    const discountEl = document.querySelector('.cart-discount-value');
    const totalEl = document.querySelector('.cart-total-value');
    
    if (subtotalEl) {
        subtotalEl.textContent = `₹${subtotal.toFixed(2)}`;
    }
    
    if (shippingEl && totalEl) {
        // Get shipping cost and calculate final total
        const shipping = parseFloat(shippingEl.textContent.replace('₹', '')) || 0;
        const discount = discountEl ? parseFloat(discountEl.textContent.replace('₹', '')) || 0 : 0;
        const total = subtotal + shipping - discount;
        
        totalEl.textContent = `₹${total.toFixed(2)}`;
    }
    
    // Update cart count in header
    const cartCount = document.querySelector('.cart-count');
    if (cartCount) {
        cartCount.textContent = cartItems.length;
        
        if (cartItems.length === 0) {
            cartCount.style.display = 'none';
        }
    }
}

/**
 * Calculate cart total
 */
function initCartTotal() {
    // This is called on page load
    const cartTotalSection = document.querySelector('.cart-summary');
    
    if (cartTotalSection) {
        updateCartTotals();
    }
}




/**
 * Handle address selection in checkout
 */
function initAddressSelection() {
    const addressRadios = document.querySelectorAll('input[name="address_id"]');
    const newAddressFields = document.querySelector('.new-address-fields');
    
    if (addressRadios.length > 0 && newAddressFields) {
        // Hide/show new address form based on selection
        addressRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'new') {
                    newAddressFields.style.display = 'block';
                    
                    // Make fields required
                    newAddressFields.querySelectorAll('input').forEach(input => {
                        if (!input.classList.contains('optional-field')) {
                            input.setAttribute('required', 'required');
                        }
                    });
                } else {
                    newAddressFields.style.display = 'none';
                    
                    // Remove required attribute
                    newAddressFields.querySelectorAll('input').forEach(input => {
                        input.removeAttribute('required');
                    });
                }
            });
        });
        
        // Initialize on page load
        const checkedAddress = document.querySelector('input[name="address_id"]:checked');
        if (checkedAddress) {
            if (checkedAddress.value === 'new') {
                newAddressFields.style.display = 'block';
                
                // Make fields required
                newAddressFields.querySelectorAll('input').forEach(input => {
                    if (!input.classList.contains('optional-field')) {
                        input.setAttribute('required', 'required');
                    }
                });
            } else {
                newAddressFields.style.display = 'none';
            }
        }
    }
}

/**
 * Handle payment method selection
 */
function initPaymentMethodSelection() {
    const paymentMethods = document.querySelectorAll('.payment-method');
    
    if (paymentMethods.length > 0) {
        paymentMethods.forEach(method => {
            method.addEventListener('click', function() {
                // Uncheck all other methods
                paymentMethods.forEach(m => {
                    m.classList.remove('active');
                    const radio = m.querySelector('input[type="radio"]');
                    if (radio) radio.checked = false;
                });
                
                // Select this method
                this.classList.add('active');
                const radio = this.querySelector('input[type="radio"]');
                if (radio) radio.checked = true;
                
                // Show relevant payment fields
                const paymentForms = document.querySelectorAll('.payment-form');
                const selectedForm = document.getElementById(`${radio.value}-form`);
                
                paymentForms.forEach(form => {
                    form.style.display = 'none';
                });
                
                if (selectedForm) {
                    selectedForm.style.display = 'block';
                }
                
                // Handle special case for COD
                const pincodeInput = document.querySelector('input[name="pincode"]');
                const codNotAvailableMsg = document.querySelector('.cod-not-available');
                
                if (radio.value === 'cod' && pincodeInput && codNotAvailableMsg) {
                    // Check if COD is available for this pincode
                    const pincode = pincodeInput.value;
                    
                    if (pincode) {
                        fetch(`/products/check-delivery/${pincode}/`)
                            .then(response => response.json())
                            .then(data => {
                                if (!data.cod_available) {
                                    codNotAvailableMsg.style.display = 'block';
                                    radio.checked = false;
                                    this.classList.remove('active');
                                } else {
                                    codNotAvailableMsg.style.display = 'none';
                                }
                            })
                            .catch(error => {
                                console.error('Error:', error);
                            });
                    }
                }
            });
        });
    }
}
