from django.db import models

class Report(models.Model):
    report_id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=255,null=True,blank=True)  # null=True add kiya
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # description = models.TextField(blank=True)

    def __str__(self):
        return self.file_name or f"Report {self.report_id}"  # Handle agar file_name null ho

    def get_absolute_url(self):
        return f"/media/reports/{self.file_name}" if self.file_name else "#"  # Handle null case
# from django.db import models

# class Report(models.Model):
#     report_id = models.AutoField(primary_key=True)
#     file_name = models.CharField(max_length=255,unique=True)  # e.g., custom_design_report_1.pdf
#     uploaded_at = models.DateTimeField(auto_now_add=True)
#     description = models.TextField(blank=True)

#     def __str__(self):
#         return self.file_name

#     def get_absolute_url(self):
#         return f"/media/reports/{self.file_name}"

