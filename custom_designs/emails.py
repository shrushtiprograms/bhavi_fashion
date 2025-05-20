from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_order_completion_email(design):
    subject = f"Your Custom Design #{design.id} is Ready!"
    context = {
        'design': design,
        'user': design.user,
        'estimated_delivery': design.estimated_delivery.strftime('%d %b %Y')
    }
    
    html_message = render_to_string('custom_designs/emails/order_ready.html', context)
    text_message = render_to_string('custom_designs/emails/order_ready.txt', context)
    
    send_mail(
        subject,
        text_message,
        settings.DEFAULT_FROM_EMAIL,
        [design.user.email],
        html_message=html_message
    )

def send_shipping_notification(design):
    subject = f"Your Design #{design.id} Has Been Shipped"
    context = {
        'design': design,
        'user': design.user,
        'estimated_delivery': design.estimated_delivery.strftime('%d %b %Y')
    }
    
    html_message = render_to_string('custom_designs/order_shipped.html', context)
    text_message = render_to_string('custom_designs/order_shipped.txt', context)
    
    send_mail(
        subject,
        text_message,
        settings.DEFAULT_FROM_EMAIL,
        [design.user.email],
        html_message=html_message
    )