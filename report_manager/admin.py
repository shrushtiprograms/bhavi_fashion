from django.contrib import admin
from .models import Report
from django.utils.safestring import mark_safe
from django.utils import timezone
from datetime import timedelta

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('report_id', 'file_name', 'uploaded_at', 'view_site_link')

    def view_site_link(self, obj):
        if obj.file_name:
            thirty_days_ago = timezone.now() - timedelta(days=30)
            if obj.uploaded_at < thirty_days_ago:
                link = f'<a href="/media/reports/{obj.file_name}" target="_blank">View Old Report</a>'
            else:
                link = f'<a href="/media/reports/{obj.file_name}" target="_blank">View New Report</a>'
        else:
            link = '<a href="#" target="_blank">-</a>'
        return mark_safe(link)

    view_site_link.short_description = 'View Site'
