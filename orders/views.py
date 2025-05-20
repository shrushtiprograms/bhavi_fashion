from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
import uuid
import json
import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import razorpay
from products.models import Product, ProductVariant
from .models import Cart, CartItemNew, Order, OrderItem, Payment, RazorpayPayment
from accounts.models import Address
from .services import PaymentService
from .utils import generate_invoice_pdf

from django.utils.html import strip_tags
from django.core.paginator import Paginator
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
logger = logging.getLogger(__name__)

def calculate_cart_totals(cart_items):
    """
    Calculate cart subtotal, discount, shipping, tax, and total
    """
    subtotal = sum(item.product.current_price * item.quantity for item in cart_items)

    # Could apply dynamic shipping and tax rules here
    shipping = Decimal('99') if subtotal < Decimal('999') else Decimal('0')
    tax_rate = Decimal('0.18')  # 5% tax
    tax = subtotal * tax_rate

    discount = Decimal('0')

    total = subtotal + shipping + tax - discount

    return {
        'subtotal': subtotal,
        'discount': discount,
        'shipping': shipping,
        'tax': tax,
        'total': total
    }
def update_tracking(order):
    if order.tracking_number and order.carrier == "Shiprocket":
        try:
            response = requests.get(
                f"https://apiv2.shiprocket.in/v1/tracking/{order.tracking_number}",
                headers={"Authorization": f"Bearer {settings.SHIPROCKET_TOKEN}"}
            )
            data = response.json()
            if data['tracking_data']['track_status']:
                order.order_status = data['tracking_data']['shipment_status'].lower()
                order.estimated_delivery = data['tracking_data'].get('edd')
                order.save()
        except Exception as e:
            logger.error(f"Shiprocket tracking failed for {order.order_number}: {str(e)}")

def track_order(request):
    order = None
    error = None
    if request.method == 'POST':
        order_number = request.POST.get('order_number')
        email = request.POST.get('email')
        try:
            order = get_object_or_404(Order, order_number=order_number, user__email=email)
            logger.info(f"Order {order_number} tracked by {email}")
        except:
            error = "Order not found. Please check your order number and email."
            logger.warning(f"Failed tracking attempt for order {order_number} with email {email}")
    return render(request, 'orders/track_order.html', {'order': order, 'error': error})

@login_required
def cart(request):
    """
    View for shopping cart
    """
    totals = {
        'subtotal': Decimal('0.00'),
        'discount': Decimal('0.00'),
        'shipping': Decimal('0.00'),
        'tax': Decimal('0.00'),
        'total': Decimal('0.00'),
    }
    # Get or create cart for the user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Get all items in the cart
    cart_items = cart.items.all() if cart else []
    totals = calculate_cart_totals(cart_items)

    if cart_items:
        # Subtotal
        totals['subtotal'] = cart.subtotal or Decimal('0.00')
        
        # Shipping
        totals['shipping'] = 0 if totals['subtotal'] >= 999 else 99
        
        # Tax (18% GST)
        totals['tax'] = totals['subtotal'] * Decimal('0.18')
        
        # Total
        totals['total'] = totals['subtotal'] - totals['discount'] + totals['shipping'] + totals['tax']

    context = {
        'cart_items': cart_items,
        'totals': totals,
    }
    
    return render(request, 'orders/cart.html', {
        'cart_items': cart_items,
        'totals': totals,
    })

def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Check stock
        if not product.is_in_stock:
            return JsonResponse({
                'success': False,
                'message': f'{product.name} is out of stock'
            }, status=400)

        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            return JsonResponse({'success': False, 'message': 'Quantity must be at least 1'}, status=400)
        if quantity > product.stock:
            return JsonResponse({
                'success': False,
                'message': f'Only {product.stock} items available in stock'
            }, status=400)

        cart = get_cart(request)
        
        cart_item = CartItemNew.objects.filter(cart=cart, product=product).first()
        already_in_cart = cart_item is not None

        if already_in_cart:
            cart_item.quantity = quantity
            cart_item.save()
            # Product is already in cart, don't add again
            return JsonResponse({
                'success': True,
                'already_in_cart': True,
                'message': f'Updated cart with {quantity} {product.name}',
                'quantity': quantity
            })
        else:
            # Add product to cart
            cart_item = CartItemNew.objects.create(cart=cart, product=product, quantity=quantity)
            return JsonResponse({
                'success': True,
                'already_in_cart': False,
                'message': f'Added {product.name} to cart',
                'quantity': cart_item.quantity,
            })
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
            
def get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
                return cart
            except Cart.DoesNotExist:
                pass
        cart = Cart.objects.create()
        request.session['cart_id'] = cart.id
        return cart

def product_detail(request, id):
    """
    View to display product details
    """
    
    product = get_object_or_404(Product, id=product_id, is_active=True)
    user_cart_product_ids = []
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            user_cart_product_ids = list(cart.items.values_list('product_id', flat=True))

    # Increment product views
    product.views = product.views + 1 if hasattr(product, 'views') else 1
    product.save()

    # Get related products
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]

    # Get reviews
    reviews = product.reviews.all().order_by('-created_at')

    # Check if product is in user's wishlist
    is_in_wishlist = False
    if request.user.is_authenticated:
        is_in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'is_in_wishlist': is_in_wishlist,
        'user_cart_product_ids':user_cart_product_ids,
    }

    return render(request, 'products/detail.html', context)


@login_required
def remove_from_cart(request, item_id):
    """
    View to remove an item from cart
    """
    cart = Cart.objects.get(user=request.user)
    cart_item = get_object_or_404(CartItemNew, id=item_id, cart=cart)
    product_name = cart_item.product.name
    cart_item.delete()

    messages.success(request, f"Removed {product_name} from your cart.")

    # Redirect back to cart
    return redirect('orders:cart')


@login_required
def update_cart_quantity(request, item_id):
    """
    View to update cart item quantity
    """
    cart = Cart.objects.get(user=request.user)
    cart_item = get_object_or_404(CartItemNew, id=item_id, cart=cart)

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                raise ValueError("Quantity must be at least 1")

            # Check stock
            if quantity > cart_item.product.stock:
                quantity = cart_item.product.stock
                messages.warning(request, f"We only have {quantity} units in stock.")

            cart_item.quantity = quantity
            cart_item.save()

            # If AJAX request, return JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'quantity': quantity,
                    'subtotal': float(cart_item.subtotal),
                })

        except (ValueError, TypeError) as e:
            messages.error(request, str(e))

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })

    return redirect('orders:cart')

@login_required
def is_product_in_cart(user,product) :
    return CartItem.objects.filter(user=user,product=product).exists()


@login_required
def checkout(request):
    """
    View for checkout page
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()

    if not cart_items.exists():
        if request.method == 'POST':
            return JsonResponse({
                'success': False,
                'error': 'Your cart is empty.'
            }, status=400)
        messages.warning(request, "Your cart is empty. Please add some products before checkout.")
        return redirect('products:catalog')

    addresses = Address.objects.filter(user=request.user)
    default_address = addresses.filter(is_default=True).first()
    totals = calculate_cart_totals(cart_items)

    if request.method == 'POST':
        logger.info(f"Checkout POST received: {request.POST}")
        try:
            shipping_address_id = request.POST.get('shipping_address')
            billing_address_id = request.POST.get('billing_address')
            same_billing = request.POST.get('same_billing_address') == 'on'
            payment_method = request.POST.get('payment_method')
            customer_notes = request.POST.get('customer_notes', '')

            if not all([shipping_address_id, payment_method]):
                return JsonResponse({
                    'success': False,
                    'error': 'Please fill in all required fields.'
                }, status=400)

            shipping_address = Address.objects.get(id=shipping_address_id, user=request.user)

            if same_billing:
                billing_address = shipping_address
            else:
                if not billing_address_id:
                    return JsonResponse({
                        'success': False,
                        'error': 'Please select a billing address.'
                    }, status=400)
                billing_address = Address.objects.get(id=billing_address_id, user=request.user)

            for cart_item in cart_items:
                if cart_item.quantity > cart_item.product.stock:
                    return JsonResponse({
                        'success': False,
                        'error': f"Insufficient stock for {cart_item.product.name}. Only {cart_item.product.stock} available."
                    }, status=400)
                if cart_item.variant and cart_item.quantity > cart_item.variant.stock:
                    return JsonResponse({
                        'success': False,
                        'error': f"Insufficient stock for {cart_item.product.name} (variant). Only {cart_item.variant.stock} available."
                    }, status=400)

            order = Order.objects.create(
                user=request.user,
                shipping_address=shipping_address,
                billing_address=billing_address,
                subtotal=totals['subtotal'],
                discount=totals['discount'],
                shipping_cost=totals['shipping'],
                tax=totals['tax'],
                total_amount=totals['total'],
                payment_method=payment_method,
                customer_notes=customer_notes,
                payment_status='pending'
            )

            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    variant=cart_item.variant,
                    quantity=cart_item.quantity,
                    price=cart_item.product.current_price,
                    total=cart_item.product.current_price * cart_item.quantity
                )

            if payment_method == 'cod':
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=totals['total'],
                    status='completed'
                )

                order.order_status = 'processing'  # Add this line
                order.payment_status = 'completed'  # Also update payment_status for consistency
                order.save()

                for cart_item in cart_items:
                    product = cart_item.product
                    product.stock -= cart_item.quantity
                    product.save()
                    if cart_item.variant:
                        variant = cart_item.variant
                        variant.stock -= cart_item.quantity
                        variant.save()


                cart_items.delete()
                send_order_confirmation_email(order)
                return redirect('orders:order_confirmation', order_id=order.id)

            else:
                razorpay_order = client.order.create({
                    'amount': int(totals['total'] * 100),
                    'currency': 'INR',
                    'receipt': f'order_{order.id}',
                    'payment_capture': 1
                })

                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=totals['total'],
                    status='pending'
                )

                RazorpayPayment.objects.create(
                    payment=payment,
                    razorpay_order_id=razorpay_order['id'],
                    status='created',
                    attempts=1,
                    last_attempt=timezone.now()
                )

                return JsonResponse({
                    'success': True,
                    'order_id': razorpay_order['id'],
                    'amount': int(totals['total'] * 100),
                    'currency': 'INR',
                    'key': settings.RAZORPAY_KEY_ID,
                    'name': 'Bhavi Fashion',
                    'description': f'Order #{order.id}',
                    'image': request.build_absolute_uri('static/images/logo.jpg'),
                    'prefill': {
                        'name': request.user.get_full_name() or request.user.username,
                        'email': request.user.email,
                        'contact': shipping_address.phone
                    },
                    'callback_url': request.build_absolute_uri(reverse('orders:payment_callback')),
                    'django_order_id': order.id
                })

        except Address.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Invalid address selected.'
            }, status=400)
        except razorpay.errors.BadRequestError as e:
            logger.error(f"Razorpay error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to initiate payment. Please try again.'
            }, status=400)
        except Exception as e:
            logger.error(f"Checkout error: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'An unexpected error occurred. Please try again.'
            }, status=500)

    context = {
        'cart_items': cart_items,
        'addresses': addresses,
        'default_address': default_address,
        'totals': totals,
    }
    return render(request, 'orders/checkout.html', context)

@login_required
def order_confirmation(request, order_id):
    """
    View for order confirmation page
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    context = {
        'order': order,
    }

    return render(request, 'orders/confirmation.html', context)


@login_required
def order_history(request):

    orders = Order.objects.filter(user=request.user).order_by('-created_at')
     # Pagination
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'orders': page_obj.object_list, 
    }

    return render(request, 'orders/history.html', context)


@login_required
def order_detail(request, order_id):
    """
    View to display order details
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # Get product IDs the user has reviewed
    reviewed_product_ids = Review.objects.filter(
        user=request.user,
        product__in=[item.product.id for item in order.items.all()]
    ).values_list('product_id', flat=True)
    context = {
        'order': order,
        'reviewed_product_ids': list(reviewed_product_ids),
    }
    return render(request, 'orders/detail.html', context)

@login_required
def payment(request, order_id):
    """
    View to handle payment for an order using Razorpay
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Check if payment is already completed
    if order.payment_status == 'paid':
        messages.info(request, "This order has already been paid for.")
        return redirect('orders:order_detail', order_id=order_id)

    # Create or get payment
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'payment_method': 'card',
            'amount': order.total_amount,
            'status': 'pending'
        }
    )

    # Check if we have valid Razorpay credentials
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        logger.error(f"Missing Razorpay credentials for Order #{order.order_number}")
        messages.error(request, "Payment gateway configuration error. Please contact support.")
        return redirect('orders:order_detail', order_id=order_id)

    # Create Razorpay order if it doesn't exist
    try:
        # Check if we already have a Razorpay order for this payment
        try:
            razorpay_payment = RazorpayPayment.objects.get(payment=payment)
            razorpay_order_id = razorpay_payment.razorpay_order_id
        except RazorpayPayment.DoesNotExist:
            # Create new Razorpay order
            razorpay_order = PaymentService.create_razorpay_order(
                order.order_number,
                float(order.total_amount)
            )

            if not razorpay_order:
                logger.error(f"Failed to create Razorpay order for Order #{order.order_number}")
                messages.error(request, "Failed to initialize payment. Please try again later.")
                return redirect('orders:order_detail', order_id=order_id)

            razorpay_order_id = razorpay_order['id']

            # Create RazorpayPayment record
            razorpay_payment = RazorpayPayment.objects.create(
                payment=payment,
                razorpay_order_id=razorpay_order_id,
                status='created',
                attempts=1,
                last_attempt=timezone.now()
            )

        # Prepare context for the payment page
        context = {
            'order': order,
            'payment': payment,
            'razorpay_payment': razorpay_payment,
            'razorpay_order_id': razorpay_order_id,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'callback_url': request.build_absolute_uri(reverse('orders:payment_callback')),
        }

        return render(request, 'orders/payment.html', context)

    except Exception as e:
        logger.error(f"Error initializing payment for Order #{order.order_number}: {str(e)}")
        messages.error(request, "Failed to initialize payment. Please try again later.")
        return redirect('orders:order_detail', order_id=order_id)


# In orders/views.py, after the payment() view and before payment_success()

# @csrf_exempt
# def payment_callback(request):
#     if request.method == 'POST':
#         try:
#             payment_id = request.POST.get('razorpay_payment_id')
#             razorpay_order_id = request.POST.get('razorpay_order_id')
#             signature = request.POST.get('razorpay_signature')

#             # Verify payment
#             params_dict = {
#                 'razorpay_order_id': razorpay_order_id,
#                 'razorpay_payment_id': payment_id,
#                 'razorpay_signature': signature
#             }

#             client.utility.verify_payment_signature(params_dict)

#             # Get payment record
#             razorpay_payment = RazorpayPayment.objects.get(razorpay_order_id=razorpay_order_id)
#             payment = razorpay_payment.payment
#             order = payment.order

#             # Update payment status
#             payment.status = 'completed'
#             payment.transaction_id = payment_id
#             payment.save()

#             # Update order status
#             order.payment_status = 'paid'
#             order.save()

#             # Update Razorpay payment record
#             razorpay_payment.razorpay_payment_id = payment_id
#             razorpay_payment.signature = signature
#             razorpay_payment.status = 'captured'
#             razorpay_payment.save()

#             # Send confirmation email
#             send_order_confirmation_email(order)

#             return JsonResponse({
#                 'success': True,
#                 'redirect_url': reverse('orders:payment_success', args=[order.order_number])
#             })

#         except Exception as e:
#             logger.error(f"Payment callback error: {str(e)}")
#             return JsonResponse({'success': False, 'error': str(e)})

#     return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def payment_success(request, order_number):
    """
    View for payment success page
    """
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    context = {
        'order': order,
    }

    return render(request, 'orders/payment_success.html', context)

@csrf_exempt
def payment_callback(request):
    if request.method == 'POST':
        try:
            logger.info("Payment callback started")
            # Verify payment signature
            params = {
                'razorpay_order_id': request.POST['razorpay_order_id'],
                'razorpay_payment_id': request.POST['razorpay_payment_id'],
                'razorpay_signature': request.POST['razorpay_signature']
            }
            client.utility.verify_payment_signature(params)

            # Get payment record
            razorpay_payment = RazorpayPayment.objects.get(razorpay_order_id=params['razorpay_order_id'])
            payment = razorpay_payment.payment
            order = payment.order

            # Update payment status
            payment.status = 'completed'
            payment.transaction_id = params['razorpay_payment_id']
            payment.save()

            # Update Razorpay payment record
            razorpay_payment.razorpay_payment_id = params['razorpay_payment_id']
            razorpay_payment.signature = params['razorpay_signature']
            razorpay_payment.status = 'paid'
            razorpay_payment.save()

            # Update order status
            order.payment_status = 'paid'
            order.order_status = 'confirmed'
            order.save()

            # Update stock
            for item in order.items.all():
                product = item.product
                product.stock -= item.quantity
                product.save()
                if item.variant:
                    variant = item.variant
                    variant.stock -= item.quantity
                    variant.save()

            # Clear cart
            CartItemNew.objects.filter(cart__user=order.user).delete()

            # Send confirmation email
            send_order_confirmation_email(order)
            logger.info(f"Payment callback processed for order #{order.order_number}")

            context = {
                'order': order,
            }
            return render(request, 'orders/payment_success.html', context)

        except razorpay.errors.SignatureVerificationError:
            logger.error("Razorpay signature verification failed")
            return JsonResponse({
                'success': False,
                'error': 'Payment verification failed'
            }, status=400)
        except Exception as e:
            logger.error(f"Payment processing error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    return redirect('orders:checkout')

@login_required
def payment_failure(request, order_number):
    """
    View for payment failure page
    """
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
    except Order.DoesNotExist:
        return render(request, 'orders/payment_failure.html', {
            'error': f'No order found with number {order_number}',
            'order_number': order_number
        })
    return render(request, 'orders/payment_failure.html', {'order': order})

@receiver(post_save, sender=Order)
def send_status_update_email(sender, instance, created, **kwargs):
    if created:
        return  # Handled by checkout view
    if instance.order_status in ['shipped', 'out_for_delivery', 'delivered']:
        try:
            subject = f"Order #{instance.order_number} Status Update"
            context = {'order': instance, 'user': instance.user}
            html_content = render_to_string('orders/email_status_update.html', context)
            text_content = strip_tags(html_content)
            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [instance.user.email],
                reply_to=[settings.DEFAULT_FROM_EMAIL]
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            logger.info(f"Status update email sent for order #{instance.order_number}")
        except Exception as e:
            logger.error(f"Failed to send status update email for order #{instance.order_number}: {str(e)}")

# At the bottom of orders/views.py, after all view functions

def send_order_confirmation_email(order):
    try:
        # Validate recipient email
        if not order.user or not order.user.email:
            logger.error(f"No user or email associated with order #{order.order_number}")
            return False

        recipient_email = order.user.email
        logger.info(f"Preparing to send email to {recipient_email} for order #{order.order_number}")

        # Prepare email content
        subject = f"Your Order #{order.order_number} Confirmation & Invoice"
        context = {'order': order, 'user': order.user}
        html_content = render_to_string('orders/email_confirmation.html', context)
        text_content = strip_tags(html_content)

        # Generate PDF invoice
        logger.info("Generating PDF invoice...")
        pdf_content = generate_invoice_pdf(order)
        if not pdf_content:
            logger.error("PDF generation failed")
            raise Exception("Failed to generate PDF invoice")

        # Create email message
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            reply_to=[settings.DEFAULT_FROM_EMAIL]
        )
        email.attach_alternative(html_content, "text/html")

        # Attach PDF
        email.attach(
            filename=f"Invoice_{order.order_number}.pdf",
            content=pdf_content,
            mimetype="application/pdf"
        )

        # Add headers
        email.extra_headers = {
            'X-Mailer': 'Django',
            'X-Priority': '1',
            'Importance': 'High'
        }

        # Send email and check result
        logger.info("Attempting to send email...")
        email_sent = email.send(fail_silently=False)
        logger.info(f"Email send() returned: {email_sent}")

        if email_sent == 0:
            raise Exception("Email send() returned 0 (not sent)")

        logger.info(f"Order confirmation email sent for order #{order.order_number}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email for order #{order.order_number}: {str(e)}", exc_info=True)
        return False
    
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/detail.html', {'order': order})