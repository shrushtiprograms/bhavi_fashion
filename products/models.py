from django.db import models
from django.utils.text import slugify
from accounts.models import User
from django.db.models import Avg

def product_image_path(instance, filename):
    """
    Function to define upload path for product images
    """
    return f'products/{instance.product.id}/{filename}'


class Category(models.Model):
    """
    Model for product categories
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='children')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def get_products(self):
        """Get all products in this category"""
        return self.products.filter(is_active=True)


class Product(models.Model):
    """
    Model for products
    """


    name = models.CharField(max_length=200)
    design_id = models.CharField(max_length=20,unique=True,help_text="Unique ID for the design ")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.IntegerField(default=0)
    available_sizes = models.CharField(max_length=255, blank=True, null=True,
                                       help_text="Comma separated sizes: S,M,L,XL")
    colors = models.CharField(max_length=255, blank=True, null=True, help_text="Comma separated colors: Red,Blue,Green")
    material = models.CharField(max_length=100, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.design_id:
            self.design_id = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def current_price(self):
        """Return the current price (discounted if available)"""
        if self.discount_price:
            return self.discount_price
        return self.price

    @property
    def discount_percentage(self):
        """Calculate the discount percentage"""
        if self.discount_price:
            discount = ((self.price-self.discount_price )/self.price)* 100
            return int(discount)
        return 0

    @property
    def primary_image(self):
        """Get the primary image for the product"""
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary
        return self.images.first()

    @property
    def avg_rating(self):
        """Get the average rating for the product"""
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    @property
    def rating_count(self):
        """Get the number of ratings for the product"""
        return self.reviews.count()

    def get_sizes_list(self):
        """Get the list of available sizes"""
        if not self.available_sizes:
            return []
        return [size.strip() for size in self.available_sizes.split(',')]

    def get_colors_list(self):
        """Get the list of available colors"""
        if not self.colors:
            return []
        return [color.strip() for color in self.colors.split(',')]


class ProductImage(models.Model):
    """
    Model for product images
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_image_path)
    is_primary = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductVariant(models.Model):
    """
    Model for product variants (size/color combinations)
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=10, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    stock = models.IntegerField(default=0)
    image = models.ForeignKey(ProductImage, on_delete=models.SET_NULL, blank=True, null=True, related_name='variants')

    class Meta:
        unique_together = ('product', 'size', 'color')

    def __str__(self):
        variant_str = ''
        if self.size:
            variant_str += f"Size: {self.size}"
        if self.color:
            variant_str += f" Color: {self.color}" if variant_str else f"Color: {self.color}"
        return variant_str or "Default Variant"


class ProductReview(models.Model):
    """
    Model for product reviews
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=100)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.rating} stars by {self.user.username}"


class Wishlist(models.Model):
    """
    Model for user wishlist items
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='in_wishlists')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username}'s wishlist - {self.product.name}"