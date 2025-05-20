from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
import json
import csv
import datetime

from accounts.models import User
from products.models import Category, Product, ProductImage, Wishlist
from orders.models import Order, OrderItem
from custom_designs.models import CustomDesign
from bulk_orders.models import BulkOrder
from tailor_jobs.models import TailorApplication
from django.contrib.admin.views.decorators import staff_member_required
from report_manager.models import Report


def admin_login(request):
    """
    View for admin login
    """
    if request.user.is_authenticated:
        if request.user.is_admin():
            return redirect('admin_dashboard:dashboard')
        else:
            messages.error(request, "You don't have permission to access the admin dashboard.")
            return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None and user.is_admin():
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('admin_dashboard:dashboard')
        else:
            messages.error(request, "Invalid credentials or insufficient permissions.")

    return render(request, 'account/login.html')


@login_required
def dashboard(request):
    """
    View for admin dashboard
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')

    # Get counts for dashboard overview
    products_count = Product.objects.filter(is_active=True).count()
    low_stock_count = Product.objects.filter(stock__lt=5, is_active=True).count()
    orders_count = Order.objects.all().count()
    pending_orders_count = Order.objects.filter(order_status='pending').count()

    custom_designs_count = CustomDesign.objects.filter(status='pending').count()
    bulk_orders_count = BulkOrder.objects.filter(status='new').count()
    tailor_applications_count = TailorApplication.objects.filter(status='applied').count()

    # Get recent orders
    recent_orders = Order.objects.all().order_by('-created_at')[:5]

    # Get sales data for chart (last 7 days)
    today = timezone.now().date()
    sales_data = []
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        orders_on_day = Order.objects.filter(created_at__date=day)

        sales_amount = orders_on_day.aggregate(total=Sum('total_amount'))['total'] or 0
        orders_count = orders_on_day.count()

        sales_data.append({
            'date': day.strftime('%d %b'),
            'amount': float(sales_amount),
            'orders': orders_count
        })

    context = {
        'products_count': products_count,
        'low_stock_count': low_stock_count,
        'orders_count': orders_count,
        'pending_orders_count': pending_orders_count,
        'custom_designs_count': custom_designs_count,
        'bulk_orders_count': bulk_orders_count,
        'tailor_applications_count': tailor_applications_count,
        'recent_orders': recent_orders,
        'sales_data': json.dumps(sales_data)
    }

    return render(request, 'admin_dashboard/dashboard.html', context)


@login_required
def products(request):
    """
    View to manage products
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')

    # Filter options
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')
    stock_filter = request.GET.get('stock')

    products = Product.objects.all()

    # Apply filters
    if category_id:
        products = products.filter(category_id=category_id)

    if search_query:
        products = products.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    if stock_filter == 'low':
        products = products.filter(stock__lt=5)
    elif stock_filter == 'out':
        products = products.filter(stock=0)

    # Order products
    products = products.order_by('-created_at')

    # Pagination
    paginator = Paginator(products, 10)  # 10 products per page
    page = request.GET.get('page')
    products = paginator.get_page(page)

    # Get categories for filter
    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
        'stock_filter': stock_filter
    }

    return render(request, 'admin_dashboard/products.html', context)


@login_required
def add_product(request):
    """
    View to add a new product
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        discount_price = request.POST.get('discount_price')
        stock = request.POST.get('stock', 0)
        available_sizes = request.POST.get('available_sizes')
        colors = request.POST.get('colors')
        material = request.POST.get('material')
        is_featured = request.POST.get('is_featured') == 'on'
        is_active = request.POST.get('is_active') == 'on'

        # Validate required fields
        if not all([name, category_id, description, price]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('admin_dashboard:add_product')

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            messages.error(request, "Invalid category.")
            return redirect('admin_dashboard:add_product')

        from django.utils.text import slugify

        # Create product
        product = Product(
            name=name,
            slug=slugify(name),
            category=category,
            description=description,
            price=price,
            discount_price=discount_price if discount_price else None,
            stock=stock,
            available_sizes=available_sizes,
            colors=colors,
            material=material,
            is_featured=is_featured,
            is_active=is_active
        )
        product.save()

        # Handle image uploads
        images = request.FILES.getlist('images')
        for i, image in enumerate(images):
            product_image = ProductImage(
                product=product,
                image=image,
                is_primary=(i == 0)  # First image is primary
            )
            product_image.save()

        messages.success(request, f"Product '{name}' added successfully.")
        return redirect('admin_dashboard:products')

    # GET request
    categories = Category.objects.all()

    context = {
        'categories': categories,
    }

    return render(request, 'admin_dashboard/add_product.html', context)


@login_required
def edit_product(request, product_id):
    """
    View to edit a product
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        discount_price = request.POST.get('discount_price')
        stock = request.POST.get('stock', 0)
        available_sizes = request.POST.get('available_sizes')
        colors = request.POST.get('colors')
        material = request.POST.get('material')
        is_featured = request.POST.get('is_featured') == 'on'
        is_active = request.POST.get('is_active') == 'on'

        # Validate required fields
        if not all([name, category_id, description, price]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('admin_dashboard:edit_product', product_id=product_id)

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            messages.error(request, "Invalid category.")
            return redirect('admin_dashboard:edit_product', product_id=product_id)

        # Update product
        product.name = name
        product.category = category
        product.description = description
        product.price = price
        product.discount_price = discount_price if discount_price else None
        product.stock = stock
        product.available_sizes = available_sizes
        product.colors = colors
        product.material = material
        product.is_featured = is_featured
        product.is_active = is_active
        product.save()

        # Handle image uploads
        images = request.FILES.getlist('images')
        for i, image in enumerate(images):
            # If there are existing images, don't set new ones as primary
            is_primary = False
            if i == 0 and not product.images.filter(is_primary=True).exists():
                is_primary = True

            product_image = ProductImage(
                product=product,
                image=image,
                is_primary=is_primary
            )
            product_image.save()

        # Handle primary image selection
        primary_image_id = request.POST.get('primary_image')
        if primary_image_id:
            try:
                primary_image = ProductImage.objects.get(id=primary_image_id, product=product)
                ProductImage.objects.filter(product=product).update(is_primary=False)
                primary_image.is_primary = True
                primary_image.save()
            except ProductImage.DoesNotExist:
                pass

        # Handle image deletion
        delete_images = request.POST.getlist('delete_images')
        if delete_images:
            ProductImage.objects.filter(id__in=delete_images, product=product).delete()

        messages.success(request, f"Product '{name}' updated successfully.")
        return redirect('admin_dashboard:products')

    # GET request
    categories = Category.objects.all()
    images = product.images.all()

    context = {
        'product': product,
        'categories': categories,
        'images': images,
    }

    return render(request, 'admin_dashboard/edit_product.html', context)


@login_required
def delete_product(request, product_id):
    """
    View to delete a product
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product_name = product.name

        # Delete product images
        for image in product.images.all():
            image.image.delete()  # Delete the physical file
            image.delete()  # Delete the image record

        # Delete the product
        product.delete()

        messages.success(request, f"Product '{product_name}' has been deleted.")
        return redirect('admin_dashboard:products')

    return render(request, 'admin_dashboard/delete_product.html', {'product': product})


@login_required
def categories(request):
    """
    View to manage categories
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')

    categories = Category.objects.all().order_by('name')

    context = {
        'categories': categories
    }

    return render(request, 'admin_dashboard/categories.html', context)


@login_required
def add_category(request):
    """
    View to add a new category
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'

        # Validate required fields
        if not name:
            messages.error(request, "Category name is required.")
            return redirect('admin_dashboard:add_category')

        from django.utils.text import slugify

        # Create category
        category = Category(
            name=name,
            slug=slugify(name),
            description=description,
            is_active=is_active
        )

        # Handle image upload
        if 'image' in request.FILES:
            category.image = request.FILES['image']

        category.save()

        messages.success(request, f"Category '{name}' added successfully.")
        return redirect('admin_dashboard:categories')

    return render(request, 'admin_dashboard/add_category.html')


@login_required
def edit_category(request, category_id):
    """
    View to edit a category
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'

        # Validate required fields
        if not name:
            messages.error(request, "Category name is required.")
            return redirect('admin_dashboard:edit_category', category_id=category_id)

        # Update category
        category.name = name
        category.description = description
        category.is_active = is_active

        # Handle image upload
        if 'image' in request.FILES:
            # Delete old image if it exists
            if category.image:
                category.image.delete()
            category.image = request.FILES['image']

        category.save()

        messages.success(request, f"Category '{name}' updated successfully.")
        return redirect('admin_dashboard:categories')

    context = {
        'category': category
    }

    return render(request, 'admin_dashboard/edit_category.html', context)


@login_required
def delete_category(request, category_id):
    """
    View to delete a category
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    category = get_object_or_404(Category, id=category_id)

    # Check if the category has associated products
    has_products = Product.objects.filter(category=category).exists()

    if request.method == 'POST':
        if has_products and request.POST.get('confirm') != 'yes':
            messages.error(request, "Please confirm deletion of category with associated products.")
            return redirect('admin_dashboard:delete_category', category_id=category_id)

        category_name = category.name

        # Delete the category image
        if category.image:
            category.image.delete()

        # Delete the category
        category.delete()

        messages.success(request, f"Category '{category_name}' has been deleted.")
        return redirect('admin_dashboard:categories')

    context = {
        'category': category,
        'has_products': has_products
    }

    return render(request, 'admin_dashboard/delete_category.html', context)


@login_required
def orders(request):
    """
    View to manage orders
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')

    # Filter options
    status_filter = request.GET.get('status', '')
    payment_filter = request.GET.get('payment', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search_query = request.GET.get('search', '')

    orders = Order.objects.all()

    # Apply filters
    if status_filter:
        orders = orders.filter(order_status=status_filter)

    if payment_filter:
        orders = orders.filter(payment_method=payment_filter)

    if date_from:
        try:
            date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__gte=date_from)
        except ValueError:
            pass

    if date_to:
        try:
            date_to = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__lte=date_to)
        except ValueError:
            pass

    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(shipping_address__name__icontains=search_query) |
            Q(shipping_address__phone__icontains=search_query)
        )

    # Order by created_at (newest first)
    orders = orders.order_by('-created_at')

    # Pagination
    paginator = Paginator(orders, 20)  # 20 orders per page
    page = request.GET.get('page')
    orders = paginator.get_page(page)

    context = {
        'orders': orders,
        'status_filter': status_filter,
        'payment_filter': payment_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
        'status_choices': Order.STATUS_CHOICES,
        'payment_choices': Order.PAYMENT_METHODS
    }

    return render(request, 'admin_dashboard/orders.html', context)


@login_required
def order_detail(request, order_number):
    """
    View to display order details
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    order = get_object_or_404(Order, order_number=order_number)
    order_items = order.items.all()

    context = {
        'order': order,
        'order_items': order_items,
        'status_choices': Order.STATUS_CHOICES
    }

    return render(request, 'admin_dashboard/order_detail.html', context)


@login_required
def update_order_status(request, order_number):
    """
    View to update order status
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    if request.method != 'POST':
        return redirect('admin_dashboard:order_detail', order_number=order_number)

    order = get_object_or_404(Order, order_number=order_number)
    new_status = request.POST.get('order_status')

    if new_status not in dict(Order.STATUS_CHOICES):
        messages.error(request, "Invalid status selected.")
        return redirect('admin_dashboard:order_detail', order_number=order_number)

    # Update order status
    order.order_status = new_status
    order.save()

    # If status is changed to "delivered", also update payment status for COD orders
    if new_status == 'delivered' and order.payment_method == 'cod' and order.payment_status == 'pending':
        order.payment_status = 'paid'
        order.save()

    # Send email notification to customer
    subject = f'Your Order {order.order_number} Status Updated'
    message = f'''
    Dear {order.user.get_full_name() or order.user.username},

    Your order status has been updated to: {dict(Order.STATUS_CHOICES)[new_status]}

    Order Number: {order.order_number}
    Total Amount: ₹{order.total_amount}

    Thank you for shopping with Bhavi India Fashion!
    '''

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            fail_silently=False,
        )
    except Exception as e:
        # Log error but continue
        print(f"Error sending email: {e}")

    messages.success(request, f"Order status updated to '{dict(Order.STATUS_CHOICES)[new_status]}'.")
    return redirect('admin_dashboard:order_detail', order_number=order_number)


@login_required
def custom_designs(request):
    """
    View to manage custom design requests
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')

    # Filter options
    status_filter = request.GET.get('status', '')
    design_type_filter = request.GET.get('design_type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search_query = request.GET.get('search', '')

    designs = CustomDesign.objects.all()

    # Apply filters
    if status_filter:
        designs = designs.filter(status=status_filter)

    if design_type_filter:
        designs = designs.filter(design_type=design_type_filter)

    if date_from:
        try:
            date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            designs = designs.filter(created_at__date__gte=date_from)
        except ValueError:
            pass

    if date_to:
        try:
            date_to = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
            designs = designs.filter(created_at__date__lte=date_to)
        except ValueError:
            pass

    if search_query:
        designs = designs.filter(
            Q(name__icontains=search_query) |
            Q(contact__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )

    # Order by created_at (newest first)
    designs = designs.order_by('-created_at')

    # Pagination
    paginator = Paginator(designs, 20)  # 20 items per page
    page = request.GET.get('page')
    designs = paginator.get_page(page)

    context = {
        'designs': designs,
        'status_filter': status_filter,
        'design_type_filter': design_type_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
        'status_choices': CustomDesign.STATUS_CHOICES,
        'design_type_choices': CustomDesign.DESIGN_TYPE_CHOICES
    }

    return render(request, 'admin_dashboard/custom_designs.html', context)


@login_required
def custom_design_detail(request, design_id):
    """
    View to display custom design details
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    design = get_object_or_404(CustomDesign, id=design_id)

    context = {
        'design': design,
        'status_choices': CustomDesign.STATUS_CHOICES
    }

    return render(request, 'admin_dashboard/custom_design_detail.html', context)


@login_required
def update_custom_design_status(request, design_id):
    """
    View to update custom design status
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    if request.method != 'POST':
        return redirect('admin_dashboard:custom_design_detail', design_id=design_id)

    design = get_object_or_404(CustomDesign, id=design_id)
    new_status = request.POST.get('status')
    rejection_reason = request.POST.get('rejection_reason', '')

    if new_status not in dict(CustomDesign.STATUS_CHOICES):
        messages.error(request, "Invalid status selected.")
        return redirect('admin_dashboard:custom_design_detail', design_id=design_id)

    # Update status
    design.status = new_status

    # If rejected, save the reason
    if new_status == 'rejected' and rejection_reason:
        design.rejection_reason = rejection_reason

    design.save()

    # Send email notification to customer
    subject = f'Your Custom Design Request Status Updated'
    message = f'''
    Dear {design.user.get_full_name() or design.user.username},

    Your custom design request for {design.get_design_type_display_name()} has been updated to: {dict(CustomDesign.STATUS_CHOICES)[new_status]}

    '''

    if new_status == 'rejected' and rejection_reason:
        message += f'''
        Reason for rejection: {rejection_reason}

        We encourage you to submit a new request with the suggested changes.
        '''

    message += '''
    Thank you for choosing Bhavi India Fashion!
    '''

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [design.user.email],
            fail_silently=False,
        )
    except Exception as e:
        # Log error but continue
        print(f"Error sending email: {e}")

    messages.success(request, f"Custom design status updated to '{dict(CustomDesign.STATUS_CHOICES)[new_status]}'.")
    return redirect('admin_dashboard:custom_design_detail', design_id=design_id)


@login_required
def bulk_orders(request):
    """
    View to manage bulk order inquiries
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')

    # Filter options
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search_query = request.GET.get('search', '')

    orders = BulkOrder.objects.all()

    # Apply filters
    if status_filter:
        orders = orders.filter(status=status_filter)

    if date_from:
        try:
            date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__gte=date_from)
        except ValueError:
            pass

    if date_to:
        try:
            date_to = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__lte=date_to)
        except ValueError:
            pass

    if search_query:
        orders = orders.filter(
            Q(business_name__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(contact__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(product_type__icontains=search_query)
        )

    # Order by created_at (newest first)
    orders = orders.order_by('-created_at')

    # Pagination
    paginator = Paginator(orders, 20)  # 20 items per page
    page = request.GET.get('page')
    orders = paginator.get_page(page)

    context = {
        'bulk_orders': orders,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
        'status_choices': BulkOrder.STATUS_CHOICES
    }

    return render(request, 'admin_dashboard/bulk_orders.html', context)


@login_required
def bulk_order_detail(request, order_id):
    """
    View to display bulk order details
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    order = get_object_or_404(BulkOrder, id=order_id)

    context = {
        'order': order,
        'status_choices': BulkOrder.STATUS_CHOICES
    }

    return render(request, 'admin_dashboard/bulk_order_detail.html', context)


@login_required
def update_bulk_order_status(request, order_id):
    """
    View to update bulk order status
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    if request.method != 'POST':
        return redirect('admin_dashboard:bulk_order_detail', order_id=order_id)

    order = get_object_or_404(BulkOrder, id=order_id)
    new_status = request.POST.get('status')
    rejection_reason = request.POST.get('rejection_reason', '')

    if new_status not in dict(BulkOrder.STATUS_CHOICES):
        messages.error(request, "Invalid status selected.")
        return redirect('admin_dashboard:bulk_order_detail', order_id=order_id)

    # Update status
    order.status = new_status

    # If rejected, save the reason
    if new_status == 'rejected' and rejection_reason:
        order.rejection_reason = rejection_reason

    order.save()

    # Send email notification to customer
    subject = f'Your Bulk Order Inquiry Status Updated'
    message = f'''
    Dear {order.contact_person},

    Your bulk order inquiry for {order.product_type} ({order.quantity} units) has been updated to: {dict(BulkOrder.STATUS_CHOICES)[new_status]}

    '''

    if new_status == 'rejected' and rejection_reason:
        message += f'''
        Reason: {rejection_reason}

        We encourage you to submit a new inquiry with the suggested changes.
        '''
    elif new_status == 'accepted':
        message += '''
        Our team will be in touch with you shortly to discuss the next steps.
        '''

    message += '''
    Thank you for your interest in Bhavi India Fashion!
    '''

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            fail_silently=False,
        )
    except Exception as e:
        # Log error but continue
        print(f"Error sending email: {e}")

    messages.success(request, f"Bulk order status updated to '{dict(BulkOrder.STATUS_CHOICES)[new_status]}'.")
    return redirect('admin_dashboard:bulk_order_detail', order_id=order_id)


@login_required
def tailor_applications(request):
    """
    View to manage tailor applications
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')

    # Filter options
    status_filter = request.GET.get('status', '')
    experience_filter = request.GET.get('experience', '')
    work_preference_filter = request.GET.get('work_preference', '')
    search_query = request.GET.get('search', '')

    applications = TailorApplication.objects.all()

    # Apply filters
    if status_filter:
        applications = applications.filter(status=status_filter)

    if experience_filter:
        applications = applications.filter(experience=experience_filter)

    if work_preference_filter:
        applications = applications.filter(work_preference=work_preference_filter)

    if search_query:
        applications = applications.filter(
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(skills__icontains=search_query)
        )

    # Order by created_at (newest first)
    applications = applications.order_by('-created_at')

    # Pagination
    paginator = Paginator(applications, 20)  # 20 items per page
    page = request.GET.get('page')
    applications = paginator.get_page(page)

    context = {
        'applications': applications,
        'status_filter': status_filter,
        'experience_filter': experience_filter,
        'work_preference_filter': work_preference_filter,
        'search_query': search_query,
        'status_choices': TailorApplication.STATUS_CHOICES,
        'experience_choices': TailorApplication.EXPERIENCE_CHOICES,
        'work_preference_choices': TailorApplication.WORK_PREFERENCE_CHOICES
    }

    return render(request, 'admin_dashboard/tailor_applications.html', context)


@login_required
def tailor_application_detail(request, application_id):
    """
    View to display tailor application details
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    application = get_object_or_404(TailorApplication, id=application_id)

    context = {
        'application': application,
        'status_choices': TailorApplication.STATUS_CHOICES
    }

    return render(request, 'admin_dashboard/tailor_application_detail.html', context)


@login_required
def update_tailor_application_status(request, application_id):
    """
    View to update tailor application status
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    if request.method != 'POST':
        return redirect('admin_dashboard:tailor_application_detail', application_id=application_id)

    application = get_object_or_404(TailorApplication, id=application_id)
    new_status = request.POST.get('status')
    rejection_reason = request.POST.get('rejection_reason', '')

    if new_status not in dict(TailorApplication.STATUS_CHOICES):
        messages.error(request, "Invalid status selected.")
        return redirect('admin_dashboard:tailor_application_detail', application_id=application_id)

    # Update status
    application.status = new_status

    # If rejected, save the reason
    if new_status == 'rejected' and rejection_reason:
        application.rejection_reason = rejection_reason

    application.save()

    # If the application is assigned, create a user account with tailor role if not exists
    if new_status == 'assigned' and not application.user:
        try:
            # Check if a user with this phone number exists
            user = User.objects.filter(phone=application.phone).first()

            if not user:
                # Create a new user with tailor role
                import random
                import string

                # Generate a random password
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

                # Create username from name (lowercase, no spaces)
                username = application.name.lower().replace(' ', '')

                # Check if username exists, add a random number if it does
                if User.objects.filter(username=username).exists():
                    username = f"{username}{random.randint(100, 999)}"

                # Create the user
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=application.name.split(' ')[0],
                    last_name=' '.join(application.name.split(' ')[1:]) if len(application.name.split(' ')) > 1 else '',
                    phone=application.phone,
                    role='tailor'
                )

                # Send credentials to the tailor
                subject = 'Your Tailor Account at Bhavi India Fashion'
                message = f'''
                Dear {application.name},

                Congratulations! Your application to join our tailor network has been approved.

                We have created an account for you with the following credentials:

                Username: {username}
                Password: {password}

                Please login at: http://localhost:8000/accounts/login/

                After login, you can view your assignments and update your profile.

                Welcome to the Bhavi India Fashion family!
                '''

                try:
                    # Send email if email exists, otherwise rely on admin to communicate
                    if hasattr(user, 'email') and user.email:
                        send_mail(
                            subject,
                            message,
                            settings.DEFAULT_FROM_EMAIL,
                            [user.email],
                            fail_silently=False,
                        )
                except Exception as e:
                    # Log error but continue
                    print(f"Error sending email: {e}")

            # Associate the user with the application
            application.user = user
            application.save()

        except Exception as e:
            print(f"Error creating tailor user account: {e}")

    messages.success(request,
                     f"Tailor application status updated to '{dict(TailorApplication.STATUS_CHOICES)[new_status]}'.")
    return redirect('admin_dashboard:tailor_application_detail', application_id=application_id)


@login_required
def sales_report(request):
    """
    View to generate sales reports
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    # Filter options
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    category_id = request.GET.get('category', '')
    payment_method = request.GET.get('payment_method', '')

    # Default to current month if no dates provided
    if not date_from and not date_to:
        today = timezone.now().date()
        date_from = today.replace(day=1).strftime('%Y-%m-%d')
        date_to = today.strftime('%Y-%m-%d')

    # Process filters
    try:
        if date_from:
            date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
        else:
            date_from_obj = None

        if date_to:
            date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
        else:
            date_to_obj = None
    except ValueError:
        messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
        date_from_obj = None
        date_to_obj = None

    # Base query
    orders = Order.objects.filter(payment_status='paid')

    # Apply filters
    if date_from_obj:
        orders = orders.filter(created_at__date__gte=date_from_obj)

    if date_to_obj:
        orders = orders.filter(created_at__date__lte=date_to_obj)

    if payment_method:
        orders = orders.filter(payment_method=payment_method)

    # Calculate total sales
    total_sales = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    orders_count = orders.count()

    # Get order items for product-level analysis
    order_items = OrderItem.objects.filter(order__in=orders)

    # Apply category filter to order items
    if category_id:
        order_items = order_items.filter(product__category_id=category_id)

    # Sales by category
    from django.db.models import F

    category_sales = []
    if order_items.exists():
        category_data = order_items.values(
            'product__category__name'
        ).annotate(
            total=Sum(F('product_price') * F('quantity')),
            count=Count('id')
        ).order_by('-total')

        for item in category_data:
            if item['product__category__name']:  # Skip None values
                category_sales.append({
                    'category': item['product__category__name'],
                    'total': item['total'],
                    'count': item['count']
                })

    # Sales by product (top 10)
    product_sales = []
    if order_items.exists():
        product_data = order_items.values(
            'product_name'
        ).annotate(
            total=Sum(F('product_price') * F('quantity')),
            count=Sum('quantity')
        ).order_by('-total')[:10]

        for item in product_data:
            product_sales.append({
                'product': item['product_name'],
                'total': item['total'],
                'count': item['count']
            })

    # Sales by date
    date_sales = []
    if orders.exists():
        date_data = orders.values(
            'created_at__date'
        ).annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('created_at__date')

        for item in date_data:
            date_sales.append({
                'date': item['created_at__date'].strftime('%Y-%m-%d'),
                'total': item['total'],
                'count': item['count']
            })

    # Export as CSV if requested
    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="sales_report_{date_from}_{date_to}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Date', 'Order Number', 'Customer', 'Payment Method', 'Total Amount'])

        for order in orders.order_by('created_at'):
            writer.writerow([
                order.created_at.strftime('%Y-%m-%d'),
                order.order_number,
                order.user.get_full_name() or order.user.username,
                order.get_payment_method_display(),
                order.total_amount
            ])

        return response

    # Get categories for filter
    categories = Category.objects.all()

    context = {
        'date_from': date_from,
        'date_to': date_to,
        'category_id': category_id,
        'payment_method': payment_method,
        'categories': categories,
        'payment_choices': Order.PAYMENT_METHODS,
        'total_sales': total_sales,
        'orders_count': orders_count,
        'category_sales': category_sales,
        'product_sales': product_sales,
        'date_sales': json.dumps([{
            'date': item['date'],
            'total': float(item['total']),
            'count': item['count']
        } for item in date_sales])
    }

    return render(request, 'admin_dashboard/sales_report.html', context)


@login_required
def inventory_report(request):
    """
    View to generate inventory reports
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    # Filter options
    category_id = request.GET.get('category', '')
    stock_filter = request.GET.get('stock', '')
    search_query = request.GET.get('search', '')

    products = Product.objects.all()

    # Apply filters
    if category_id:
        products = products.filter(category_id=category_id)

    if stock_filter == 'low':
        products = products.filter(stock__lt=5)
    elif stock_filter == 'out':
        products = products.filter(stock=0)
    elif stock_filter == 'available':
        products = products.filter(stock__gt=0)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Order by stock (lowest first)
    products = products.order_by('stock')

    # Export as CSV if requested
    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventory_report.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'Category', 'Price', 'Stock', 'Status'])

        for product in products:
            writer.writerow([
                product.id,
                product.name,
                product.category.name,
                product.price,
                product.stock,
                'Active' if product.is_active else 'Inactive'
            ])

        return response

    # Get categories for filter
    categories = Category.objects.all()

    # Calculate inventory statistics
    total_products = products.count()
    total_stock = products.aggregate(total=Sum('stock'))['total'] or 0
    low_stock_count = products.filter(stock__lt=5).count()
    out_of_stock_count = products.filter(stock=0).count()

    # Calculate inventory value
    inventory_value = 0
    for product in products:
        inventory_value += product.price * product.stock

    # Inventory by category
    inventory_by_category = []
    category_data = products.values(
        'category__name'
    ).annotate(
        total_stock=Sum('stock'),
        total_value=Sum(F('price') * F('stock')),
        product_count=Count('id')
    ).order_by('category__name')

    for item in category_data:
        if item['category__name']:  # Skip None values
            inventory_by_category.append({
                'category': item['category__name'],
                'total_stock': item['total_stock'],
                'total_value': item['total_value'],
                'product_count': item['product_count']
            })

    # Paginate products
    paginator = Paginator(products, 20)  # 20 products per page
    page = request.GET.get('page')
    products = paginator.get_page(page)

    context = {
        'products': products,
        'categories': categories,
        'category_id': category_id,
        'stock_filter': stock_filter,
        'search_query': search_query,
        'total_products': total_products,
        'total_stock': total_stock,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'inventory_value': inventory_value,
        'inventory_by_category': inventory_by_category
    }

    return render(request, 'admin_dashboard/inventory_report.html', context)


@login_required
def customer_report(request):
    """
    View to generate customer reports
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    # Filter options
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search_query = request.GET.get('search', '')

    # Default to last 30 days if no dates provided
    if not date_from and not date_to:
        today = timezone.now().date()
        date_from = (today - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        date_to = today.strftime('%Y-%m-%d')

    # Process filters
    try:
        if date_from:
            date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
        else:
            date_from_obj = None

        if date_to:
            date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
        else:
            date_to_obj = None
    except ValueError:
        messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
        date_from_obj = None
        date_to_obj = None

    # Get all customers
    customers = User.objects.filter(role='customer')

    if search_query:
        customers = customers.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    # Get orders in date range
    orders_query = Order.objects.filter(payment_status='paid')

    if date_from_obj:
        orders_query = orders_query.filter(created_at__date__gte=date_from_obj)

    if date_to_obj:
        orders_query = orders_query.filter(created_at__date__lte=date_to_obj)

    # Get customer orders in date range
    customer_data = []
    for customer in customers:
        customer_orders = orders_query.filter(user=customer)
        order_count = customer_orders.count()

        if order_count > 0 or 'all' in request.GET:
            total_spent = customer_orders.aggregate(total=Sum('total_amount'))['total'] or 0
            last_order = customer_orders.order_by('-created_at').first()

            customer_data.append({
                'user': customer,
                'order_count': order_count,
                'total_spent': total_spent,
                'last_order_date': last_order.created_at if last_order else None,
                'last_order_number': last_order.order_number if last_order else None
            })

    # Sort by total spent (highest first)
    customer_data.sort(key=lambda x: x['total_spent'], reverse=True)

    # Export as CSV if requested
    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="customer_report_{date_from}_{date_to}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Username', 'Name', 'Email', 'Phone', 'Orders', 'Total Spent', 'Last Order Date'])

        for data in customer_data:
            customer = data['user']
            writer.writerow([
                customer.username,
                customer.get_full_name(),
                customer.email,
                customer.phone,
                data['order_count'],
                data['total_spent'],
                data['last_order_date'].strftime('%Y-%m-%d') if data['last_order_date'] else 'N/A'
            ])

        return response

    # Paginate customer data
    paginator = Paginator(customer_data, 20)  # 20 customers per page
    page = request.GET.get('page')
    customer_data = paginator.get_page(page)

    # Calculate totals
    total_customers = customers.count()
    active_customers = len([c for c in customer_data.object_list if c['order_count'] > 0])

    context = {
        'customer_data': customer_data,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
        'total_customers': total_customers,
        'active_customers': active_customers
    }

    return render(request, 'admin_dashboard/customer_report.html', context)


@login_required
def wishlist_overview(request):
    """
    View to display wishlist overview
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    # Get most wishlisted products
    wishlist_data = Wishlist.objects.values(
        'product__id',
        'product__name',
        'product__slug',
        'product__price',
        'product__discount_price',
        'product__stock'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:20]

    # Get product images
    for item in wishlist_data:
        product_id = item['product__id']
        try:
            product = Product.objects.get(id=product_id)
            primary_image = product.images.filter(is_primary=True).first()
            if primary_image:
                item['image_url'] = primary_image.image.url
            else:
                item['image_url'] = None
        except Product.DoesNotExist:
            item['image_url'] = None

    context = {
        'wishlist_data': wishlist_data
    }

    return render(request, 'admin_dashboard/wishlist_overview.html', context)


@login_required
def cart_overview(request):
    """
    View to display cart overview
    """
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    # Get most carted products
    cart_data = CartItem.objects.values(
        'product__id',
        'product__name',
        'product__slug',
        'product__price',
        'product__discount_price',
        'product__stock'
    ).annotate(
        count=Count('id'),
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:20]

    # Get product images
    for item in cart_data:
        product_id = item['product__id']
        try:
            product = Product.objects.get(id=product_id)
            primary_image = product.images.filter(is_primary=True).first()
            if primary_image:
                item['image_url'] = primary_image.image.url
            else:
                item['image_url'] = None
        except Product.DoesNotExist:
            item['image_url'] = None

    # Get abandoned carts (older than 1 day)
    yesterday = timezone.now() - datetime.timedelta(days=1)
    abandoned_carts = CartItem.objects.filter(updated_at__lt=yesterday).values(
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name'
    ).annotate(
        items_count=Count('id'),
        total_value=Sum(F('product__price') * F('quantity'))
    ).order_by('-total_value')[:10]

    context = {
        'cart_data': cart_data,
        'abandoned_carts': abandoned_carts
    }

    return render(request, 'admin_dashboard/cart_overview.html', context)
@staff_member_required  # सिर्फ admin users एक्सेस कर सकें
def report_list(request):
    reports = Report.objects.all().order_by('-created_at')  # सभी रिपोर्ट्स लोड करें
    return render(request, 'admin/report_list.html', {'reports': reports})