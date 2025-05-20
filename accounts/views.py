from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, AddressForm, ProfileUpdateForm
from .models import Address
from orders.models import Order
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import random
from django.core.cache import cache
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from products.models import Wishlist
from custom_designs.models import CustomDesign
from bulk_orders.models import BulkOrder
from django.http import HttpResponse,JsonResponse
from django.urls import get_resolver, reverse
from tailor_jobs.models import TailorApplication
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from django.views.decorators.cache import never_cache
User = get_user_model()

def debug_urls(request):
    urlconf = get_resolver()
    url_patterns = set()  # Use a set to avoid duplicates
    
    # Handle namespaced URLs
    for ns, value in urlconf.namespace_dict.items():
        # Safely unpack with default values if fewer than 3 elements
        if isinstance(value, tuple):
            patterns = value[0]  # First element is always the URL patterns
            app_name = value[1] if len(value) > 1 else None
            namespace = value[2] if len(value) > 2 else ns
            
            for pattern in patterns.url_patterns:
                if hasattr(pattern, 'name') and pattern.name:
                    url_patterns.add(f"{namespace}:{pattern.name}")
    
    # Include non-namespaced URLs
    for name in urlconf.reverse_dict.keys():
        if isinstance(name, str) and ':' not in name:
            url_patterns.add(name)
    
    # Sort and return the list
    return HttpResponse("<br>".join(sorted(url_patterns)))

def contact_view(request):
    return render(request, 'accounts/contactus.html')


def about(request):
    return render(request, 'accounts/aboutus.html')

def support(request):
    return render(request, 'accounts/customer_support.html')    

@csrf_protect
def contact_submit(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            subject = request.POST.get('subject')
            message = request.POST.get('message')

            # Validate data
            if not all([name, email, subject, message]):
                return JsonResponse({'success': False, 'message': 'All required fields must be filled.'}, status=400)

            # Send email to admin (customize as needed)
            send_mail(
                
                f'Contact Form: {subject}',
                f'Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}',
                email,
                ['xabc52520@gmail.com'],
                fail_silently=False,
            )

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    return render(request,'accounts/contactus.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate a 6-digit OTP
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            request.session['reset_email'] = email
            request.session['reset_otp'] = otp
            request.session.set_expiry(300)  # OTP expires in 5 minutes

            # Send OTP via email
            subject = 'Password Reset OTP - Bhavi India Fashion'
            message = f"""
            Hello {user.username},

            Your OTP for password reset is: {otp}

            Use this OTP to reset your password at: http://127.0.0.1:8000/accounts/reset_password/

            This OTP is valid for 5 minutes. If you didn’t request this, ignore this email.

            Sincerely,
            The Bhavi India Fashion Team
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'OTP has been sent to your email.')
            return redirect('accounts:reset_password')
        except User.DoesNotExist:
            messages.error(request, 'No user found with this email.')
    return render(request, 'accounts/password_reset.html')

@login_required
def set_default_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    # Reset existing default
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    # Set new default
    address.is_default = True
    address.save()
    return redirect('accounts:profile')

def reset_password(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/reset_password.html')

        stored_otp = request.session.get('reset_otp')
        email = request.session.get('reset_email')

        if not stored_otp or not email:
            messages.error(request, 'Session expired. Please request a new OTP.')
            return redirect('accounts:password_reset')

        if otp == stored_otp:
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                # Clear session data
                del request.session['reset_otp']
                del request.session['reset_email']
                messages.success(request, 'Password reset successfully. Please login.')
                return redirect('accounts:login')
            except User.DoesNotExist:
                messages.error(request, 'Something went wrong. Please try again.')
        else:
            messages.error(request, 'Invalid OTP.')
    return render(request, 'accounts/reset_password.html')

def register_view(request):
    """
    View for user registration
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful, you are now logged in.")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please check the form.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})

# @never_cache
# def login_view(request):
#     if request.user.is_authenticated:
#         if request.user.is_admin():
#             if request.user.is_staff or request.user.is_superuser:
#                 return redirect('/admin/')
#             return redirect('admin_dashboard:dashboard')
#         return redirect(reverse('home'))

#     # Initialize session variables
#     if 'failed_attempts' not in request.session:
#         request.session['failed_attempts'] = 0
#         request.session['last_failed_attempt'] = None
#         request.session['lockout_until'] = None

#     # Check lockout status
#     lockout_until = request.session.get('lockout_until')
#     if lockout_until:
#         lockout_time = timezone.datetime.fromisoformat(lockout_until)
#         if timezone.now() < lockout_time:
#             remaining_seconds = (lockout_time - timezone.now()).seconds
#             remaining_minutes = (remaining_seconds // 60) + (1 if remaining_seconds % 60 > 0 else 0)
#             error_message = f"Too many failed login attempts. Please try again in {remaining_minutes} minute{'s' if remaining_minutes != 1 else ''}."
#             if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#                 return JsonResponse({'success': False, 'message': error_message, 'lockout': True})
#             messages.warning(request, error_message)
#             return render(request, 'accounts/login.html', {'form': CustomAuthenticationForm()})
#         else:
#             # Reset lockout
#             request.session['failed_attempts'] = 0
#             request.session['last_failed_attempt'] = None
#             request.session['lockout_until'] = None

#     if request.method == 'POST':
#         form = CustomAuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 request.session['failed_attempts'] = 0
#                 request.session['last_failed_attempt'] = None
#                 request.session['lockout_until'] = None
#                 # Handle "remember me"
#                 if request.POST.get('remember_me'):
#                     request.session.set_expiry(1209600)  # 2 weeks
#                 else:
#                     request.session.set_expiry(0)  # Browser session
#                 # Determine redirect URL
#                 if user.is_admin():
#                     redirect_url = '/admin/' if user.is_staff or user.is_superuser else reverse('admin_dashboard:dashboard')
#                 else:
#                     redirect_url = request.POST.get('next') or request.GET.get('next') or reverse('home')
            
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             return JsonResponse({
#                 'success': True,
#                 'message': 'Logged in successfully.',
#                 'redirect_url': redirect_url
#             })
#         return redirect(redirect_url)
def login_view(request):
    if request.user.is_authenticated:
        # If user is already logged in, redirect to homepage or admin dashboard based on role
        if request.user.is_admin():
            if request.user.is_staff or request.user.is_superuser:
                return redirect('/admin/')
            return redirect('admin_dashboard:dashboard')
        return redirect('home')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect based on role
                if user.is_admin():
                    if user.is_staff or user.is_superuser:
                        return redirect('/admin/')
                    return redirect('admin_dashboard:dashboard')
                # Redirect to next parameter or homepage
                next_page = request.POST.get('next') or request.GET.get('next', 'home')
                messages.success(request, "Logged in successfully.")
                return redirect(next_page)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomAuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})

@login_required
def view_site_as_user(request):
    """
    Logs out the admin from the અથવા View the site as a normal user by logging out the admin session
    """
    logout(request)
    messages.info(request, "You are now viewing the site as a guest. Log in again to access your account.")
    return redirect('home')

@login_required
def logout_view(request):
    """
    View for user logout
    """
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def profile_view(request):
    """
    View for user profile
    """
    user=request.user
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=user).order_by('-created_at')
    recent_orders = orders[:2]  # For overview tab
    active_tab = request.GET.get('tab', 'overview')
    default_address = addresses.filter(is_default=True).first()
    has_tailor_application = TailorApplication.objects.filter(user=request.user).exists()
    bulk_orders = BulkOrder.objects.filter(user=request.user).order_by('-created_at')
    wishlist_items=Wishlist.objects.filter(user=request.user).select_related('product')
    custom_designs = CustomDesign.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'user': request.user,
        'orders': orders,
        'recent_orders': recent_orders,
        'default_address': request.user.addresses.filter(is_default=True).first(),
        'addresses': request.user.addresses.all(),
        'bulk_orders': bulk_orders,
        'orders': Order.objects.filter(user=request.user),
        'wishlist_items':wishlist_items,
        'custom_designs': custom_designs,
        'active_tab': active_tab,
        'has_tailor_application': has_tailor_application,
    }

    return render(request, 'accounts/profile.html', context)

@login_required
def remove_from_wishlist(request, wishlist_id):
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    wishlist_item.delete()
    messages.success(request, "Item removed from your wishlist.")
    return redirect('accounts:profile')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            # Save profile updates (e.g., first_name, last_name, phone, profile_image)
            form.save()
            

            # Handle password change
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if current_password and new_password and confirm_password:
                user = authenticate(username=request.user.username, password=current_password)
                if user is not None:
                    if new_password == confirm_password:
                        request.user.set_password(new_password)
                        request.user.save()
                        messages.success(request, "Your profile and password have been updated successfully.")
                    else:
                        messages.error(request, "New passwords do not match.")
                        return render(request, 'accounts/profile.html', {'form': form})
                else:
                    messages.error(request, "Current password is incorrect.")
                    return render(request, 'accounts/profile.html', {'form': form})
            else:
                messages.success(request, "Your profile has been updated successfully.")
            active_tab = request.POST.get('active_tab', 'overview')
            return redirect(reverse('accounts:profile') + f'?tab={active_tab}')
        else:
            messages.error(request, "Profile update failed. Please check the form.")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def address_list(request):
    active_tab = request.POST.get('active_tab', 'address')
    return redirect(reverse('accounts:profile') + f'?tab={active_tab}')

@login_required
def add_address(request):
    """
    View to add a new address
    """
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Address added successfully.")
            active_tab = request.POST.get('active_tab', 'address')
            return redirect(reverse('accounts:profile') + f'?tab={active_tab}')
        else:
            messages.error(request, "Failed to add address. Please check the form.")
    else:
        form = AddressForm()

    return render(request, 'accounts/address_form.html', {'form': form, 'action': 'Add'})


@login_required
def edit_address(request, pk):
    """
    View to edit an existing address
    """
    address = get_object_or_404(Address, pk=pk, user=request.user)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully.")
            active_tab = request.POST.get('active_tab', 'address')
            return redirect(reverse('accounts:profile') + f'?tab={active_tab}')
        else:
            messages.error(request, "Failed to update address. Please check the form.")
    else:
        form = AddressForm(instance=address)

    return render(request, 'accounts/address_form.html', {'form': form, 'action': 'Edit'})


@login_required
def delete_address(request, pk):
    """
    View to delete an address
    """
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, "Address deleted successfully.")
    return redirect('accounts:address_list')


@login_required
def order_history(request):
    """
    View to display user's order history
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/order_history.html', {'orders': orders})


@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    paginator = Paginator(wishlist_items, 9)  # 9 items per page
    page_number = request.GET.get('page')
    wishlist_items = paginator.get_page(page_number)

    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'accounts/wishlist.html', context)

@login_required
def clear_wishlist(request):
    if request.method == 'POST':
        Wishlist.objects.filter(user=request.user).delete()
    return redirect('accounts:wishlist')

@login_required
def custom_designs(request):
    """
    View to display user's custom design requests
    """
    designs = CustomDesign.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/custom_designs.html', {'designs': designs})


@login_required
def bulk_orders(request):
    """
    View to display user's bulk order requests
    """
    orders = BulkOrder.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/bulk_orders.html', {'orders': orders})


def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_of_service(request):
    return render(request, 'terms_of_service.html')

def return_policy(request):
    return render(request, 'return_policy.html')