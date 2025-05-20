
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from .models import CustomDesign
from .forms import CustomDesignForm
import json
from decimal import Decimal
import logging 
import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

logger = logging.getLogger(__name__)

@login_required
def custom_design_form(request):
    if request.method == 'POST':
        form = CustomDesignForm(request.POST, request.FILES)
        if form.is_valid():
            design = form.save(commit=False)
            design.user = request.user
            design.save()
            messages.success(request, 'Your custom design request has been submitted successfully!')
            return redirect('custom_designs:details', design_id=design.id)
    else:
        form = CustomDesignForm()
    
    return render(request, 'custom_designs/custom_design_form.html', {'form': form})

@login_required
def custom_design_details(request, design_id):
    design = get_object_or_404(CustomDesign, id=design_id, user=request.user)
    
    if request.method == 'POST' and design.status == 'accepted':
        # Handle payment submission
        return handle_payment(request, design)
    
    return render(request, 'custom_designs/custom_design_details.html', {
        'design': design,
        'advance_amount': design.get_advance_amount()
    })

@require_POST
@login_required
def handle_payment(request, design):
    # In a real implementation, this would integrate with a payment gateway
    # For now, we'll simulate a successful payment
    
    design.advance_payment = design.get_advance_amount()
    design.payment_status = 'partial'
    design.save()
    
    messages.success(request, f"Advance payment of ₹{design.advance_payment} received! Your order is confirmed.")
    return redirect('custom_designs:details', design_id=design.id)

@login_required
def update_design_status(request, design_id):
    if not request.user.is_staff:
        return HttpResponseBadRequest("Unauthorized")
    
    design = get_object_or_404(CustomDesign, id=design_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        rejection_reason = request.POST.get('rejection_reason', '')
        
        if new_status not in dict(CustomDesign.STATUS_CHOICES):
            return HttpResponseBadRequest("Invalid status")
        
        design.status = new_status
        if new_status == 'rejected':
            design.rejection_reason = rejection_reason
        elif new_status == 'accepted':
            design.accepted_at = timezone.now()
        
        design.save()
        messages.success(request, f"Design status updated to {design.get_status_display()}")
        return redirect('admin:custom_designs_customdesign_changelist')
    
    return HttpResponseBadRequest("Invalid request")

@login_required
def submit_custom_design(request):
    if request.method == 'POST':
        try:
            # Extract form data
            name = request.POST.get('name')
            contact = request.POST.get('contact')
            address = request.POST.get('address')
            design_type = request.POST.get('design_type')
            other_design_type = request.POST.get('other_design_type', '')
            fabric_type = request.POST.get('fabric_type')
            selected_color = request.POST.get('selected_color')
            
            if not selected_color:
                raise ValueError("Color selection is required")

            embroidery = 'embroidery' in request.POST
            measurement_mode = request.POST.get('measurement_mode', 'static')
            quantity = int(request.POST.get('quantity', 1))
            timeline = request.POST.get('timeline')
            budget = Decimal(request.POST.get('budget'))
            notes = request.POST.get('notes', '')
            reference_image = request.FILES.get('reference_image')

            # Initialize measurement fields
            standard_size = None
            custom_measurements = {}

            def clean_measurement(value):
                if value in [None, '']:
                    return None
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return None

            # Handle measurement mode (static = standard size, dynamic = custom measurements)
            if measurement_mode == 'static':
                standard_size = request.POST.get('standard_size')
                if not standard_size:
                    raise ValueError("Standard size is required for standard size mode")
            elif measurement_mode == 'dynamic':
                # Populate custom_measurements based on design_type
                prefix = f"{design_type}_"  # e.g., "kurti_", "blouse_"
                if design_type == 'kurti':
                    custom_measurements = {
                        'shoulder': clean_measurement(request.POST.get(f'{prefix}shoulder')),
                        'chest': clean_measurement(request.POST.get(f'{prefix}chest')),
                        'waist': clean_measurement(request.POST.get(f'{prefix}waist')),
                        'hips': clean_measurement(request.POST.get(f'{prefix}hips')),
                        'top_length': clean_measurement(request.POST.get(f'{prefix}top_length')),
                        'sleeve_length': clean_measurement(request.POST.get(f'{prefix}sleeve_length'))
                    }
                elif design_type == 'blouse':
                    custom_measurements = {
                        'shoulder': clean_measurement(request.POST.get(f'{prefix}shoulder')),
                        'chest': clean_measurement(request.POST.get(f'{prefix}chest')),
                        'waist': clean_measurement(request.POST.get(f'{prefix}waist')),
                        'sleeve_length': clean_measurement(request.POST.get(f'{prefix}sleeve_length')),
                        'back_neck_depth': clean_measurement(request.POST.get(f'{prefix}back_neck_depth')),
                        'blouse_length': clean_measurement(request.POST.get(f'{prefix}blouse_length')),
                        'armhole': clean_measurement(request.POST.get(f'{prefix}armhole'))
                    }
                elif design_type == 'pant':
                    custom_measurements = {
                        'pant_length': clean_measurement(request.POST.get(f'{prefix}pant_length')),
                        'rise': clean_measurement(request.POST.get(f'{prefix}rise')),
                        'waist': clean_measurement(request.POST.get(f'{prefix}waist')),
                        'thigh': clean_measurement(request.POST.get(f'{prefix}thigh')),
                        'knee': clean_measurement(request.POST.get(f'{prefix}knee')),
                        'ankle': clean_measurement(request.POST.get(f'{prefix}ankle'))
                    }
                elif design_type == 'choli':
                    custom_measurements = {
                        'shoulder': clean_measurement(request.POST.get(f'{prefix}shoulder')),
                        'chest': clean_measurement(request.POST.get(f'{prefix}chest')),
                        'waist': clean_measurement(request.POST.get(f'{prefix}waist')),
                        'hips': clean_measurement(request.POST.get(f'{prefix}hips')),
                        'other': clean_measurement(request.POST.get(f'{prefix}other'))
                    }
                else:  # 'other' design type
                    custom_measurements = {
                        'shoulder': clean_measurement(request.POST.get(f'{prefix}shoulder')),
                        'chest': clean_measurement(request.POST.get(f'{prefix}chest')),
                        'waist': clean_measurement(request.POST.get(f'{prefix}waist')),
                        'hips': clean_measurement(request.POST.get(f'{prefix}hips')),
                        'other': request.POST.get(f'{prefix}other')  # Store as string
                    }

                # Validate that at least one measurement is provided
                if not any(value is not None for value in custom_measurements.values()):
                    raise ValueError(f"Please provide at least one measurement for {design_type}")

            # Create custom design record
            design = CustomDesign.objects.create(
                user=request.user,
                name=name,
                contact=contact,
                address=address,
                design_type=design_type,
                other_design_type=other_design_type if design_type == 'other' else None,
                fabric_type=fabric_type,
                selected_color=selected_color,
                reference_image=reference_image,
                embroidery=embroidery,
                measurement_mode=measurement_mode,
                standard_size=standard_size,
                custom_measurements=custom_measurements,
                quantity=quantity,
                timeline=timeline,
                budget=budget,
                notes=notes,
                status='pending'
            )

            messages.success(request, 'Your custom design request has been submitted successfully!')
            return redirect('custom_designs:details', design_id=design.id)

        except Exception as e:
            logger.error(f"Error submitting custom design: {str(e)}")
            messages.error(request, f"Error submitting design: {str(e)}")
            return redirect('custom_designs:form')

    return redirect('custom_designs:form')

@login_required
def custom_design_details(request, design_id):
    """
    View to display custom design details
    """
    design = get_object_or_404(CustomDesign, id=design_id)

    status_message = ''
    if design.status == 'rejected':
        status_message = f"Rejected - Reason: {design.rejection_reason}"
    elif design.status == 'accepted':
        status_message = "Accepted! Please proceed with payment to confirm your order."
    
    return render(request, 'custom_designs/custom_design_details.html', {
        'design': design,
        'status_message': status_message,
        'advance_amount': design.get_advance_amount()  # Show 30% payment
    })



def get_size_chart(request, design_type):
    """
    View to get size chart data for a specific design type
    """
    size_charts = {
        'kurti': {
            'XS': {'bust': 32, 'waist': 26, 'hips': 35, 'length': 38},
            'S': {'bust': 34, 'waist': 28, 'hips': 37, 'length': 39},
            'M': {'bust': 36, 'waist': 30, 'hips': 39, 'length': 40},
            'L': {'bust': 38, 'waist': 32, 'hips': 41, 'length': 41},
            'XL': {'bust': 40, 'waist': 34, 'hips': 43, 'length': 42},
            'XXL': {'bust': 42, 'waist': 36, 'hips': 45, 'length': 43},
        },
        'blouse': {
            'XS': {'bust': 32, 'waist': 26, 'length': 16},
            'S': {'bust': 34, 'waist': 28, 'length': 16.5},
            'M': {'bust': 36, 'waist': 30, 'length': 17},
            'L': {'bust': 38, 'waist': 32, 'length': 17.5},
            'XL': {'bust': 40, 'waist': 34, 'length': 18},
            'XXL': {'bust': 42, 'waist': 36, 'length': 18.5},
        },
        'choli': {
            'XS': {'bust': 32, 'waist': 26, 'length': 14},
            'S': {'bust': 34, 'waist': 28, 'length': 14.5},
            'M': {'bust': 36, 'waist': 30, 'length': 15},
            'L': {'bust': 38, 'waist': 32, 'length': 15.5},
            'XL': {'bust': 40, 'waist': 34, 'length': 16},
            'XXL': {'bust': 42, 'waist': 36, 'length': 16.5},
        }
    }

    chart = size_charts.get(design_type, {})
    return JsonResponse(chart)

@require_POST
@login_required
def initiate_payment(request, design_id):
    design = get_object_or_404(CustomDesign, id=design_id, user=request.user)
    
    if design.status != 'accepted':
        return JsonResponse({'error': 'Design not approved yet'}, status=400)
    
    if design.payment_status != 'pending':
        return JsonResponse({'error': 'Payment already processed'}, status=400)
    
    try:
        # Calculate 30% advance
        advance_amount = int(float(design.budget) * 0.3 * 100)  # in paise
        
        # Create Razorpay order
        order_data = {
            'amount': advance_amount,
            'currency': 'INR',
            'receipt': f'design_advance_{design.id}',
            'payment_capture': '1',
            'notes': {
                'design_id': design.id,
                'purpose': 'design_advance'
            }
        }
        
        razorpay_order = client.order.create(data=order_data)
        
        return JsonResponse({
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': advance_amount,
            'design_id': design.id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
def payment_webhook(request):
    if request.method == 'POST':
        try:
            # Verify signature
            payload = request.body.decode('utf-8')
            received_sign = request.headers.get('X-Razorpay-Signature')
            
            client.utility.verify_webhook_signature(
                payload, 
                received_sign, 
                settings.RAZORPAY_WEBHOOK_SECRET
            )
            
            data = json.loads(payload)
            
            # Handle payment success
            if data['event'] == 'payment.captured':
                design_id = data['payload']['payment']['entity']['notes']['design_id']
                design = CustomDesign.objects.get(id=design_id)
                
                # Update payment status
                design.payment_status = 'partial'
                design.advance_payment = float(data['payload']['payment']['entity']['amount'])/100
                design.save()
                
                # Send confirmation email
                send_payment_confirmation_email(design)
                
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            return HttpResponse(status=400)
            
    return HttpResponse(status=200)

@login_required
def payment_success(request, design_id):
    design = get_object_or_404(CustomDesign, id=design_id, user=request.user)
    
    # In production, verify payment via webhook before updating status
    design.payment_status = 'partial'
    design.advance_payment = design.budget * Decimal('0.3')
    design.save()
    # Send confirmation email
    send_payment_confirmation_email(design)
    
    messages.success(request, "Advance payment received! Your order is confirmed.")
    return render(request,'custom_designs/payment_success.html', {'design': design})

    
def send_payment_confirmation_email(design):
    subject = f"Payment Confirmation for Design #{design.id}"
    html_message = render_to_string('custom_designs/emails/payment_confirmation.html', {
        'design': design,
        'user': design.user
    })
    text_message = render_to_string('custom_designs/emails/payment_confirmation.txt', {
        'design': design,
        'user': design.user
    })
    
    send_mail(
        subject,
        text_message,
        settings.DEFAULT_FROM_EMAIL,
        [design.user.email],
        html_message=html_message,
        fail_silently=False
    )