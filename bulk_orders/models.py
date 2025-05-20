from django.db import models
from accounts.models import User
from products.models import Product

class BulkOrder(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('partial', 'Advance Paid'),
        ('paid', 'Fully Paid'),
        ('refunded', 'Refunded'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bulk_orders')
    business_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)
    email = models.EmailField()
    quantity = models.PositiveIntegerField()
    budget = models.DecimalField(max_digits=10, decimal_places=2, help_text="Budget in INR")
    delivery_timeline = models.CharField(max_length=50)
    shipping_address = models.TextField()
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    rejection_reason = models.TextField(blank=True, null=True)
    advance_payment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bulk order by {self.business_name}"

    def get_advance_amount(self):
        return float(self.budget) * 0.3

class BulkOrderItem(models.Model):
    bulk_order = models.ForeignKey(BulkOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    custom_design_name = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField()
    size_color = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        if self.product and not self.custom_design_name:
            return f"{self.quantity} x {self.product.name}"
        return f"{self.quantity} x {self.custom_design_name or 'Custom Design'}"

class CustomDesignImage(models.Model):
    bulk_order_item = models.ForeignKey(BulkOrderItem, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='custom_designs/%Y/%m/%d/')

    def __str__(self):
        return f"Image for {self.bulk_order_item}"