# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from .models import CustomDesign

# @receiver(post_save, sender=CustomDesign)
# def send_status_notification(sender, instance, **kwargs):
#     if kwargs.get('created', False):
#         # New design created
#         return
        
#     # Get the previous status
#     try:
#         old_instance = CustomDesign.objects.get(pk=instance.pk)
#     except CustomDesign.DoesNotExist:
#         return
        
#     if old_instance.status != instance.status:
#         # Status changed - send email
#         subject = f"Your Custom Design Status Update - {instance.get_status_display()}"
        
#         context = {
#             'design': instance,
#             'status': instance.get_status_display(),
#             'user': instance.user
#         }
        
#         html_message = render_to_string('custom_designs/email/status_update.html', context)
#         text_message = render_to_string('custom_designs/email/status_update.txt', context)
        
#         send_mail(
#             subject,
#             text_message,
#             'noreply@bhavifashion.com',
#             [instance.user.email],
#             html_message=html_message,
#             fail_silently=True
#         )

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import CustomDesign

@receiver(post_save, sender=CustomDesign)
def send_design_status_notification(sender, instance, created, **kwargs):
    if created:
        send_mail(
            f"Design #{instance.id} Submitted",
            f"Your design has been submitted successfully.",
            settings.DEFAULT_FROM_EMAIL,
            [instance.user.email]
        )
    elif instance.status == 'accepted':
        send_mail(
            f"Design #{instance.id} Accepted",
            f"Your design has been accepted. Please pay ₹{instance.get_advance_amount()}.",
            settings.DEFAULT_FROM_EMAIL,
            [instance.user.email]
        )
    elif instance.status == 'rejected':
        send_mail(
            f"Design #{instance.id} Rejected",
            f"Your design was rejected. Reason: {instance.rejection_reason}.",
            settings.DEFAULT_FROM_EMAIL,
            [instance.user.email]
        )

def send_new_design_email(design):
    subject = f"Custom Design Submitted - #{design.id}"
    context = {
        'design': design,
        'user': design.user
    }
    
    send_template_email(
        subject,
        'custom_designs/emails/design_submitted.html',
        'custom_designs/emails/design_submitted.txt',
        context,
        [design.user.email]
    )

def send_status_update_email(design, old_status):
    subject = f"Design #{design.id} Status Update: {design.get_status_display()}"
    context = {
        'design': design,
        'old_status': old_status,
        'user': design.user
    }
    
    send_template_email(
        subject,
        'custom_designs/emails/status_update.html',
        'custom_designs/emails/status_update.txt',
        context,
        [design.user.email]
    )

def send_template_email(subject, html_template, text_template, context, recipients):
    html_message = render_to_string(html_template, context)
    text_message = render_to_string(text_template, context)
    
    send_mail(
        subject,
        text_message,
        settings.DEFAULT_FROM_EMAIL,
        recipients,
        html_message=html_message,
        fail_silently=True
    )