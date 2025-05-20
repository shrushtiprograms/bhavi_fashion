from django.db import models
from accounts.models import User


def sample_work_path(instance, filename):
    """Generate file path for sample work images"""
    return f'tailor_jobs/sample_work/{instance.user.id}/{filename}'


class TailorApplication(models.Model):
    """
    Model for tailor job applications
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('shortlisted', 'Shortlisted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tailor_applications')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    address = models.TextField()
    job_title = models.CharField(max_length=100, default="Tailor Position")
    experience = models.CharField(max_length=20)
    skills = models.CharField(max_length=255, help_text="Comma separated skills")
    other_skills = models.CharField(max_length=255, blank=True, null=True)
    work_mode = models.CharField(max_length=50)
    sample_work = models.ImageField(upload_to=sample_work_path, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.job_title} - {self.get_status_display()}"