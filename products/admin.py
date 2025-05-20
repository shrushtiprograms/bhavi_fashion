from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVariant, ProductReview, Wishlist


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 10


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    max_num = 20


class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 0
    readonly_fields = ('user', 'rating', 'title', 'comment', 'created_at')
    can_delete = False
    max_num = 0  # Don't show any empty forms


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'product_count')
    search_fields = ('name', 'description')

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
    'id', 'name', 'category','design_id', 'price', 'discount_price', 'stock', 'is_featured', 'is_active',
    'created_at')
    search_fields = ('name', 'description','design_id')
    readonly_fields = ('views', 'created_at', 'updated_at')
    inlines = [ProductImageInline, ProductVariantInline, ProductReviewInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name','design_id', 'category', 'description', 'price', 'discount_price')
        }),
        ('Product Details', {
            'fields': ('stock', 'available_sizes', 'colors', 'material')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active')
        }),
        ('Statistics', {
            'fields': ('views', 'created_at', 'updated_at')
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name',)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'stock')
    list_filter = ('size', 'color')
    search_fields = ('product__name',)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'title', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'title', 'comment')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'product__name')