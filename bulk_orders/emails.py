from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_order_completion_email(order):
    subject = f"Your Bulk order #{order.id} is Ready!"
    context = {
        'order': order,
        'user': order.user,
        'estimated_delivery': order.estimated_delivery.strftime('%d %b %Y')
    }
    
    html_message = render_to_string('bulk_orders/emails/order_ready.html', context)
    text_message = render_to_string('bulk_orders/emails/order_ready.txt', context)
    
    send_mail(
        subject,
        text_message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        html_message=html_message
    )

def send_shipping_notification(order):
    subject = f"Your order #{order.id} Has Been Shipped"
    context = {
        'order': order,
        'user': order.user,
        'estimated_delivery': order.estimated_delivery.strftime('%d %b %Y')
    }
    
    html_message = render_to_string('bulk_orders/order_shipped.html', context)
    text_message = render_to_string('bulk_orders/order_shipped.txt', context)
    
    send_mail(
        subject,
        text_message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        html_message=html_message
    )