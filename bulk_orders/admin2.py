from django.contrib import admin
from .models import BulkOrder, BulkOrderItem, CustomDesignImage
from django.utils.html import format_html

@admin.register(BulkOrder)
class BulkOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'business_name', 'contact', 'email', 'quantity', 'budget', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['business_name', 'contact_person', 'email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'business_name', 'contact_person', 'contact', 'email')
        }),
        ('Details', {
            'fields': ('quantity', 'budget', 'delivery_timeline', 'shipping_address', 'notes')
        }),
        ('Status', {
            'fields': ('status', 'payment_status', 'advance_payment', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(BulkOrderItem)
class BulkOrderItemAdmin(admin.ModelAdmin):
    list_display = ['bulk_order', 'product_name', 'custom_design_name', 'quantity', 'size_color']
    list_filter = ['bulk_order__status']
    search_fields = ['product__name', 'custom_design_name']
    readonly_fields = ['bulk_order']

    def product_name(self, obj):
        return obj.product.name if obj.product else 'N/A'
    product_name.short_description = 'Product'

@admin.register(CustomDesignImage)
class CustomDesignImageAdmin(admin.ModelAdmin):
    list_display = ['bulk_order_item', 'image_preview', 'image']
    list_filter = ['bulk_order_item__bulk_order__status']
    search_fields = ['bulk_order_item__custom_design_name']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width:100px;"/>', obj.image.url)
        return 'No Image'
    image_preview.short_description = 'Image Preview'