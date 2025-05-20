from django.contrib import admin
from .models import TailorApplication


@admin.register(TailorApplication)
class TailorApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'experience', 'work_mode', 'status', 'created_at')
    list_filter = ('experience', 'work_mode', 'status', 'created_at')
    search_fields = ('name', 'phone', 'address', 'skills')
    readonly_fields = ('created_at','updated_at')


    fieldsets = (
        ('Applicant Information', {
            'fields': ('user', 'name', 'phone', 'address')
        }),
        ('Skills & Experience', {
            'fields': ('job_title', 'experience', 'skills', 'other_skills', 'work_mode', 'sample_work')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Application Status', {
            'fields': ('status', 'rejection_reason', 'created_at', 'updated_at')
        }),
    )