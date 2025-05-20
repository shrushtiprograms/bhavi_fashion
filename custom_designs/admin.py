# from django.contrib import admin
# from .models import CustomDesign


# class CustomDesignAdmin(admin.ModelAdmin):
#     list_display = ('user', 'name', 'design_type', 'status', 'created_at')
#     list_filter = ('design_type', 'status', 'created_at')
#     search_fields = ('user__username', 'name', 'contact')
#     readonly_fields = ('created_at',)
    
#     fieldsets = (
#         ('Customer Information', {
#             'fields': ('user', 'name', 'contact', 'address')
#         }),
#         ('Design Details', {
#             'fields': ('design_type', 'other_design_type', 'fabric_type', 'color', 'reference_image', 'embroidery')
#         }),
#         ('Measurements', {
#             'fields': ('measurement_mode', 'size_inputs')
#         }),
#         ('Order Details', {
#             'fields': ('quantity', 'timeline', 'budget', 'notes')
#         }),
#         ('Status', {
#             'fields': ('status', 'rejection_reason', 'created_at')
#         }),
#     )


# admin.site.register(CustomDesign, CustomDesignAdmin)


from django.contrib import admin
from .models import CustomDesign
from django.utils.html import format_html

class CustomDesignAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'design_type_display', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'design_type', 'created_at')
    search_fields = ('user__username', 'name', 'contact', 'id')
    readonly_fields = ('created_at', 'updated_at', 'accepted_at')
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'name', 'contact', 'address')
        }),
        ('Design Details', {
            'fields': ('design_type', 'other_design_type', 'fabric_type', 
                        'reference_image', 'embroidery')
        }),
        ('Measurements', {
            'fields': ('measurement_mode', 'size_inputs')
        }),
        ('Order Details', {
            'fields': ('quantity', 'timeline', 'budget', 'notes')
        }),
        ('Status & Payment', {
            'fields': ('status', 'rejection_reason', 'payment_status', 'advance_payment')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'accepted_at')
        }),
    )
    
    def design_type_display(self, obj):
        return obj.get_design_type_display()
    design_type_display.short_description = 'Design Type'
    
    def color_display(self, obj):
        return format_html(
            '<span style="display: inline-block; width: 20px; height: 20px; background-color: {}; border: 1px solid #ddd; margin-right: 5px;"></span> {}',
            obj.get_color_hex(),
            obj.get_color_display()
        )
    color_display.short_description = 'Color'

@admin.action(description='Mark selected designs as completed')
def mark_completed(modeladmin, request, queryset):
    for design in queryset:
        design.completion_status = 'ready'
        design.estimated_delivery = timezone.now() + timezone.timedelta(days=7)  # 7 days from now
        design.save()
        
        # Send completion email
        send_order_completion_email(design)

class CustomDesignAdmin(admin.ModelAdmin):
    actions = [mark_completed]
    list_display = ('id', 'user', 'design_type', 'status', 'completion_status', 'estimated_delivery')

admin.site.register(CustomDesign, CustomDesignAdmin)

