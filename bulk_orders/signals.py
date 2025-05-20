# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from .models import Customorder

# @receiver(post_save, sender=Customorder)
# def send_status_notification(sender, instance, **kwargs):
#     if kwargs.get('created', False):
#         # New order created
#         return
        
#     # Get the previous status
#     try:
#         old_instance = Customorder.objects.get(pk=instance.pk)
#     except Customorder.DoesNotExist:
#         return
        
#     if old_instance.status != instance.status:
#         # Status changed - send email
#         subject = f"Your Custom order Status Update - {instance.get_status_display()}"
        
#         context = {
#             'order': instance,
#             'status': instance.get_status_display(),
#             'user': instance.user
#         }
        
#         html_message = render_to_string('bulk_orders/email/status_update.html', context)
#         text_message = render_to_string('bulk_orders/email/status_update.txt', context)
        
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
from .models import BulkOrder

@receiver(post_save, sender=BulkOrder)
def send_order_status_notification(sender, instance, created, **kwargs):
    if created:
        send_mail(
            f"Order #{instance.id} Submitted",
            f"Your order has been submitted successfully.",
            settings.DEFAULT_FROM_EMAIL,
            [instance.user.email]
        )
    elif instance.status == 'accepted':
        send_mail(
            f"Order #{instance.id} Accepted",
            f"Your order has been accepted. Please pay ₹{instance.get_advance_amount()}.",
            settings.DEFAULT_FROM_EMAIL,
            [instance.user.email]
        )
    elif instance.status == 'rejected':
        send_mail(
            f"Order #{instance.id} Rejected",
            f"Your order was rejected. Reason: {instance.rejection_reason}.",
            settings.DEFAULT_FROM_EMAIL,
            [instance.user.email]
        )

def send_new_order_email(order):
    subject = f"Bulk Order Submitted - #{order.id}"
    context = {
        'order': order,
        'user': order.user
    }
    
    send_template_email(
        subject,
        'bulk_orders/emails/order_submitted.html',
        'bulk_orders/emails/order_submitted.txt',
        context,
        [order.user.email]
    )

def send_status_update_email(order, old_status):
    subject = f"Order #{order.id} Status Update: {order.get_status_display()}"
    context = {
        'order': order,
        'old_status': old_status,
        'user': order.user
    }
    
    send_template_email(
        subject,
        'bulk_orders/emails/status_update.html',
        'bulk_orders/emails/status_update.txt',
        context,
        [order.user.email]
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