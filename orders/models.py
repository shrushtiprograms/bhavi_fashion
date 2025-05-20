from django.db import models
from django.utils import timezone
from django.conf import settings
from products.models import Product, ProductVariant
from accounts.models import User, Address


class Cart(models.Model):
    """
    Model representing a user's shopping cart
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart',null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders_cart'  # Explicitly setting table name

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.all())

    def add_item(self, product, quantity=1):
        item, created = CartItemNew.objects.get_or_create(
            cart=self,
            product=product,
            variant=None,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
        return item

    def __str__(self):
        return f"{self.user.username}'s Cart"

    @property
    def total_items(self):
        """Get the total number of items in the cart"""
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        """Get the subtotal of all items in the cart"""
        return sum(item.subtotal for item in self.items.all())



# Keep the original CartItem model for data migration purposes
# class CartItem(models.Model):
#     """
#     Model representing items in a user's shopping cart (Legacy model)
#     """
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, blank=True, null=True)
#     quantity = models.PositiveIntegerField(default=1)
#     added_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         unique_together = ('user', 'product', 'variant')
#         ordering = ['-added_at']

#     def __str__(self):
#         variant_str = f" ({self.variant})" if self.variant else ""
#         return f"{self.user.username}'s cart - {self.product.name}{variant_str} x {self.quantity}"

#     @property
#     def subtotal(self):
#         return self.product.current_price * self.quantity


# New model using the modified structure
class CartItemNew(models.Model):
    """
    Model representing items in a user's shopping cart (New model with Cart relationship)
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders_cartitemnew'  # Explicitly setting table name
        unique_together = ('cart', 'product', 'variant')
        ordering = ['-added_at']

    def __str__(self):
        variant_str = f" ({self.variant})" if self.variant else ""
        return f"{self.cart.user.username}'s cart - {self.product.name}{variant_str} x {self.quantity}"

    @property
    def subtotal(self):
        return self.product.current_price * self.quantity

class Order(models.Model):
    """
    Model representing customer orders
    """
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
        ('wallet', 'Wallet'),
        ('netbanking', 'Net Banking'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='shipping_orders')
    billing_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='billing_orders')

    subtotal = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    order_status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHOD_CHOICES, default='cod')

    tracking_number = models.CharField(max_length=50, blank=True, null=True)
    carrier = models.CharField(max_length=50, blank=True, null=True)  # New: e.g., "India Post", "Delhivery"
    estimated_delivery = models.DateField(blank=True, null=True)
    shipping_notes = models.TextField(blank=True, null=True)
    customer_notes = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} - {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number
            last_order = Order.objects.order_by('-id').first()
            
            if last_order:
                last_id = last_order.id
            else:
                last_id = 0

            # Format: ORD + YYMM + 5-digit sequential number
            today = timezone.now()
            prefix = f"ORD{today.strftime('%y%m')}"
            self.order_number = f"{prefix}{last_id + 1:05d}"

        # Calculate total
        self.subtotal = self.subtotal or 0
        self.discount = self.discount or 0
        self.shipping_cost = self.shipping_cost or 0
        self.tax = self.tax or 0
        self.total_amount = self.subtotal - self.discount + self.shipping_cost + self.tax

        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """
    Model representing items in an order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Historical price at time of order
    total = models.DecimalField(max_digits=10, decimal_places=2)  # price * quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity} in Order #{self.order.order_number}"

    def save(self, *args, **kwargs):
        # Calculate total
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)


class Payment(models.Model):
    """
    Model representing payment information for orders
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=15, choices=Order.PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_response = models.JSONField(blank=True, null=True)  # Store gateway response
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Order #{self.order.order_number} - {self.status}"

class RazorpayPayment(models.Model):
    """
    Model for tracking Razorpay payment information
    """
    PAYMENT_STATUS_CHOICES = [
        ('created', 'Created'),
        ('authorized', 'Authorized'),
        ('captured', 'Captured'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='razorpay_details')
    razorpay_order_id = models.CharField(max_length=100, unique=True, help_text="Razorpay Order ID")
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True, help_text="Razorpay Payment ID")
    signature = models.CharField(max_length=255, blank=True, null=True, help_text="Razorpay Signature")
    status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='created')
    razorpay_response = models.JSONField(blank=True, null=True, help_text="Complete response from Razorpay")
    attempts = models.PositiveIntegerField(default=0, help_text="Number of payment attempts")
    last_attempt = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Razorpay payment for order #{self.payment.order.order_number} - {self.status}"