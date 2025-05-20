from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.http import JsonResponse
from .models import BulkOrder, BulkOrderItem, CustomDesignImage
from .forms import BulkOrderForm
from products.models import Product
import razorpay
import json
import logging

# Setup logging
logger = logging.getLogger(__name__)

@login_required
def bulk_order_form(request):
    products = Product.objects.filter(is_active=True, stock__gt=0).select_related('category').prefetch_related('images')
    form = BulkOrderForm()
    return render(request, 'bulk_orders/bulk_order_form.html', {'form': form, 'products': products})

@login_required
def submit_bulk_order(request):
    if request.method != 'POST':
        logger.warning("Non-POST request to submit_bulk_order")
        messages.error(request, "Invalid request method.")
        return redirect('bulk_orders:form')

    form = BulkOrderForm(request.POST)
    if not form.is_valid():
        logger.error(f"Form validation failed: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
        return redirect('bulk_orders:form')

    try:
        business_name = form.cleaned_data['business_name']
        contact_person = form.cleaned_data['contact_person']
        contact = form.cleaned_data['contact']
        email = form.cleaned_data['email']
        budget = form.cleaned_data['budget']
        delivery_timeline = form.cleaned_data['delivery_timeline']
        shipping_address = form.cleaned_data['shipping_address']
        notes = form.cleaned_data['notes']

        designs_data = []
        total_quantity = 0
        i = 0
        while f'designs[{i}][type]' in request.POST:
            design_type = request.POST.get(f'designs[{i}][type]')
            product_id = request.POST.get(f'designs[{i}][product_id]')
            quantity = request.POST.get(f'designs[{i}][quantity]')
            size_color = request.POST.get(f'designs[{i}][size_color]', '')
            notes = request.POST.get(f'designs[{i}][notes]', '')
            images = request.FILES.getlist(f'designs[{i}][images]')
            custom_design_name = request.POST.get(f'designs[{i}][custom_design_name]', '')

            try:
                quantity = int(quantity)
                if quantity < 10:
                    raise ValueError(f"Design {i+1} must have at least 10 pieces.")
                total_quantity += quantity
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid quantity for design {i}: {str(e)}")
                messages.error(request, str(e))
                return redirect('bulk_orders:form')

            if design_type == 'custom' and not product_id and not images:
                logger.error(f"Custom design {i+1} missing images")
                messages.error(request, f"Custom design {i+1} requires at least one image if no product is selected.")
                return redirect('bulk_orders:form')

            if design_type == 'existing' and not product_id:
                logger.error(f"Existing design {i+1} missing product_id")
                messages.error(request, f"Existing design {i+1} requires a product selection.")
                return redirect('bulk_orders:form')

            designs_data.append({
                'type': design_type,
                'product_id': product_id,
                'quantity': quantity,
                'size_color': size_color,
                'notes': notes,
                'images': images,
                'custom_design_name': custom_design_name
            })
            i += 1

        if total_quantity < 10:
            logger.error(f"Total quantity {total_quantity} less than 10")
            messages.error(request, "Total quantity must be at least 10 pieces.")
            return redirect('bulk_orders:form')

        if not designs_data:
            logger.error("No designs provided")
            messages.error(request, "At least one design is required.")
            return redirect('bulk_orders:form')

        with transaction.atomic():
            bulk_order = BulkOrder.objects.create(
                user=request.user,
                business_name=business_name,
                contact_person=contact_person,
                contact=contact,
                email=email,
                quantity=total_quantity,
                budget=budget,
                delivery_timeline=delivery_timeline,
                shipping_address=shipping_address,
                notes=notes
            )
            logger.info(f"Created BulkOrder {bulk_order.id}")

            for design in designs_data:
                product = None
                if design['product_id']:
                    try:
                        product = Product.objects.get(id=design['product_id'])
                    except Product.DoesNotExist:
                        logger.error(f"Product {design['product_id']} not found")
                        messages.error(request, f"Invalid product ID {design['product_id']}.")
                        raise
                bulk_order_item = BulkOrderItem.objects.create(
                    bulk_order=bulk_order,
                    product=product,
                    custom_design_name=design['custom_design_name'] if design['type'] == 'custom' else '',
                    quantity=design['quantity'],
                    size_color=design['size_color'],
                    notes=design['notes']
                )
                logger.info(f"Created BulkOrderItem {bulk_order_item.id} for BulkOrder {bulk_order.id}")

                if design['type'] == 'custom' and design['images']:
                    for image in design['images']:
                        CustomDesignImage.objects.create(
                            bulk_order_item=bulk_order_item,
                            image=image
                        )
                        logger.info(f"Created CustomDesignImage for BulkOrderItem {bulk_order_item.id}")

        messages.success(request, 'Your bulk order inquiry has been submitted successfully.')
        logger.info(f"Redirecting to details for BulkOrder {bulk_order.id}")
        return redirect('bulk_orders:details', order_id=bulk_order.id)

    except Exception as e:
        logger.error(f"Error in submit_bulk_order: {str(e)}")
        messages.error(request, f"Error saving order: {str(e)}")
        return redirect('bulk_orders:form')

@login_required
def bulk_order_details(request, order_id):
    bulk_order = get_object_or_404(BulkOrder.objects.prefetch_related('items__product__category', 'items__product__images', 'items__images'), id=order_id, user=request.user)
    status_message = ''
    if bulk_order.status == 'rejected':
        status_message = f"Rejected - Reason: {bulk_order.rejection_reason}"
    elif bulk_order.status == 'accepted':
        status_message = "Accepted! Please proceed with payment to confirm your order."

    return render(request, 'bulk_orders/bulk_order_details.html', {
        'bulk_order': bulk_order,
        'items': bulk_order.items.all(),
        'status_message': status_message,
        'advance_amount': bulk_order.get_advance_amount()
    })

@login_required
def initiate_payment(request, order_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        bulk_order = get_object_or_404(BulkOrder, id=order_id, user=request.user)
        if bulk_order.status != 'accepted':
            return JsonResponse({'error': f'Order status is {bulk_order.status}, expected accepted'}, status=400)
        if bulk_order.payment_status != 'pending':
            return JsonResponse({'error': f'Payment status is {bulk_order.payment_status}, expected pending'}, status=400)

        advance_amount = int(bulk_order.get_advance_amount() * 100)  # Convert to paise
        if advance_amount < 100:
            logger.warning(f"Advance amount {advance_amount} paise for order {order_id} is below minimum")
            return JsonResponse({'error': 'Advance amount too low, minimum ₹1.00 required'}, status=400)

        RAZORPAY_KEY_ID = 'rzp_test_iA4D3D8jO4XXlG'
        RAZORPAY_KEY_SECRET = 'Fz6QDbYtS7cf4l3eErq8qZnr'
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

        order_data = {
            'amount': advance_amount,
            'currency': 'INR',
            'receipt': f'bulk_order_{bulk_order.id}',
            'payment_capture': 1
        }
        razorpay_order = client.order.create(data=order_data)

        return JsonResponse({
            'razorpay_key_id': RAZORPAY_KEY_ID,
            'razorpay_order_id': razorpay_order['id'],
            'amount': advance_amount,
            'currency': 'INR',
            'order_id': bulk_order.id
        })
    except razorpay.errors.BadRequestError as e:
        logger.error(f"Razorpay error for order {order_id}: {str(e)}")
        return JsonResponse({'error': f'Razorpay error: {str(e)}'}, status=400)
    except BulkOrder.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except Exception as e:
        logger.error(f"Payment initiation error for order {order_id}: {str(e)}")
        return JsonResponse({'error': f'Failed to initiate payment: {str(e)}'}, status=500)

@login_required
def payment_success(request, order_id):
    bulk_order = get_object_or_404(BulkOrder, id=order_id, user=request.user)
    bulk_order.advance_payment = bulk_order.get_advance_amount()
    bulk_order.payment_status = 'partial'
    bulk_order.save()
    send_payment_confirmation_email(bulk_order)
    messages.success(request, 'Payment successful!')
    return redirect('bulk_orders:details', order_id=order_id)

def send_payment_confirmation_email(bulk_order):
    subject = f"Payment Confirmation for Bulk Order #{bulk_order.id}"
    html_message = render_to_string('bulk_orders/emails/payment_confirmation.html', {
        'bulk_order': bulk_order,
        'items': bulk_order.items.all()
    })
    text_message = render_to_string('bulk_orders/emails/payment_confirmation.txt', {
        'bulk_order': bulk_order,
        'items': bulk_order.items.all()
    })
    send_mail(
        subject,
        text_message,
        settings.DEFAULT_FROM_EMAIL,
        [bulk_order.email],
        html_message=html_message,
        fail_silently=False
    )

def send_order_completion_email(bulk_order):
    subject = f"Bulk Order #{bulk_order.id} Completed"
    html_message = render_to_string('bulk_orders/emails/order_completion.html', {
        'bulk_order': bulk_order
    })
    text_message = render_to_string('bulk_orders/emails/order_completion.txt', {
        'bulk_order': bulk_order
    })
    send_mail(
        subject,
        text_message,
        settings.DEFAULT_FROM_EMAIL,
        [bulk_order.email],
        html_message=html_message,
        fail_silently=False
    )