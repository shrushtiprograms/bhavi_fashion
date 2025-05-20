from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    """
    Custom User model with role attribute to distinguish between Customers and Admins
    """
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=10, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    
    def __str__(self):
        return self.username
    
    def is_admin(self):
        return self.is_staff or self.is_superuser
    
    def is_customer(self):
        return self.role == 'customer'

    def save(self, *args, **kwargs):
        if self.is_staff or self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)


class Address(models.Model):
    """
    Model to store user addresses
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='addresses')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name}'s address at {self.city}"
    
    def save(self, *args, **kwargs):
        if self.is_default:
            # Set all other addresses of this user as not default
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
