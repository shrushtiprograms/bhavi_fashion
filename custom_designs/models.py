
from django.conf import settings
from django.db import models
from accounts.models import User
import os
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import json
from decimal import Decimal


def reference_image_path(instance, filename):
    """Generate file path for reference images"""
    ext = filename.split('.')[-1]
    filename = f"custom_design_{instance.id}_{instance.user.username}.{ext}"
    return os.path.join('custom_design_images', filename)

class CustomDesign(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in-progress', 'In Progress'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('ready', 'Ready for Delivery'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    )
    
    DESIGN_TYPE_CHOICES = (
        ('kurti', 'Kurti'),
        ('choli', 'Choli'),
        ('blouse', 'Blouse'),
        ('pant', 'Pant'),
        ('other', 'Other'),
    )
    
    MEASUREMENT_MODE_CHOICES = (
        ('static', 'Standard Size'),
        ('dynamic', 'Custom Measurements'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('partial', 'Advance Paid'),
        ('paid', 'Fully Paid'),
        ('refunded', 'Refunded'),
    )

    completion_status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='in_progress'
    )
    SIZE_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Double Extra Large'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='custom_designs')
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=10)  # Changed to CharField for phone numbers
    address = models.TextField()
    design_type = models.CharField(max_length=10, choices=DESIGN_TYPE_CHOICES)
    other_design_type = models.CharField(max_length=50, blank=True, null=True)
    fabric_type = models.CharField(max_length=100)
    color = models.JSONField(null=True, blank=True, default=dict, help_text="Stores color in hex and name format")  # Stores both hex and name
    selected_color = models.CharField(max_length=50,null=False,blank=False)
    reference_image = models.ImageField(upload_to=reference_image_path, blank=True, null=True)
    embroidery = models.BooleanField(default=False)
    measurement_mode = models.CharField(max_length=10, choices=MEASUREMENT_MODE_CHOICES,default='static')
    standard_size = models.CharField(max_length=5, choices=SIZE_CHOICES, blank=True, null=True)
    custom_measurements = models.JSONField(default=dict, blank=True)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    timeline = models.CharField(max_length=50)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    advance_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    actual_delivery = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Custom {self.get_design_type_display()} (ID: {self.id})"
    
    import json

    def get_color_display(self):
        # Ensure selected_color contains valid data (JSON format)
        try:
            color_data = json.loads(self.selected_color)  # Parse JSON
            return f"{color_data.get('name', 'Unknown')} ({color_data.get('hex')})"
        except (json.JSONDecodeError, TypeError):
            return "Invalid color"

    
    def get_color_hex(self):
    # If selected_color is a JSON string, try to parse it
        if isinstance(self.selected_color, str):
            try:
                color_data = json.loads(self.selected_color)  # Parse JSON string
                if isinstance(color_data, dict):
                    return color_data.get('hex', '#000000')  # Get hex or default to black
            except (json.JSONDecodeError, ValueError):
                # If selected_color is a plain string, just return it
                return self.selected_color if self.selected_color.startswith('#') else '#000000'


    
    def get_advance_amount(self):
        return self.budget * Decimal('0.3')  # 30% advance

    def get_design_type_display_name(self):
        if self.design_type == 'other' and self.other_design_type:
            return self.other_design_type
        return self.get_design_type_display()
