from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import User, Address
User = get_user_model()
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone', 'profile_image')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone', 'profile_image')}),
    )

class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'city', 'state', 'pincode', 'is_default_display', 'phone')
    list_filter = ('city', 'state', 'is_default')
    search_fields = ('user__username', 'name', 'city', 'pincode')
    list_per_page = 20
    
    def is_default_display(self, obj):
        return "✓" if obj.is_default else "✗"
    is_default_display.short_description = 'Is Default'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
admin.site.register(User, CustomUserAdmin)
admin.site.register(Address, AddressAdmin)
