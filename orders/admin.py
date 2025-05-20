from django.contrib import admin
from .models import Cart, CartItemNew, Order, OrderItem, Payment

class CartItemNewInline(admin.TabularInline):
    model = CartItemNew
    extra = 0
    readonly_fields = ('added_at', 'updated_at')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'variant', 'quantity', 'price', 'total')

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items', 'subtotal', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemNewInline]

# @admin.register(CartItem)
# class CartItemAdmin(admin.ModelAdmin):
#     list_display = ('user', 'product', 'variant', 'quantity', 'added_at')
#     list_filter = ('added_at',)
#     search_fields = ('user__username', 'product__name')
#     readonly_fields = ('added_at', 'updated_at')

@admin.register(CartItemNew)
class CartItemNewAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'variant', 'quantity', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('cart__user__username', 'product__name')
    readonly_fields = ('added_at', 'updated_at')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'order_status', 'payment_status', 'payment_method', 'total_amount', 'created_at')
    list_filter = ('order_status', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email')
    inlines = [OrderItemInline, PaymentInline]
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'delivered_at')
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'order_status', 'shipping_address', 'billing_address')
        }),
        ('Payment Details', {
            'fields': ('payment_status', 'payment_method')
        }),
        ('Financial', {
            'fields': ('subtotal', 'discount', 'shipping_cost', 'tax', 'total_amount')
        }),
        ('Shipping', {
            'fields': ('tracking_number', 'carrier', 'estimated_delivery', 'shipping_notes')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'delivered_at')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'variant', 'quantity', 'price', 'total')
    list_filter = ('order__created_at',)
    search_fields = ('order__order_number', 'product__name')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method', 'amount', 'status', 'transaction_id', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order__order_number', 'transaction_id')