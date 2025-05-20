from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.views.decorators.http import require_POST
from django.db.models.functions import Coalesce
from orders.models import Cart,CartItemNew
from .models import Category, Product, ProductReview, Wishlist


def product_search(request):
    query = request.GET.get('q', '')
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    else:
        products = Product.objects.all()
    
    context = {
        'products': products,
        'query': query
    }
    return render(request, 'products/search_results.html', context)

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

# views.py
def home(request):
    print("DEBUG: Entering home view")
    
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    categories = Category.objects.filter(is_active=True)
    
    # Fetch the latest 3 reviews
    try:
        testimonials = ProductReview.objects.all().order_by('-created_at')[:3]
        print(f"DEBUG: Found {testimonials.count()} testimonials")
        for idx, testimonial in enumerate(testimonials, 1):
            print(f"DEBUG: Testimonial {idx}: user={getattr(testimonial.user, 'username', 'None')}, "
                  f"rating={getattr(testimonial, 'rating', 'None')}, "
                  f"comment={getattr(testimonial, 'comment', 'None')[:50]}..., "
                  f"product={getattr(testimonial.product, 'name', 'None')}")
    except Exception as e:
        print(f"DEBUG: Error fetching testimonials: {str(e)}")
        testimonials = []
        messages.error(request, "Failed to load reviews.")
    
    # Fallback if no testimonials
    if not testimonials:
        total_reviews = ProductReview.objects.count()
        print(f"DEBUG: No testimonials found. Total reviews: {total_reviews}")
        messages.info(request, "No reviews available to display.")
    
    user_cart_product_ids = []
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            user_cart_product_ids = list(cart.items.values_list('product_id', flat=True))
    
    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist_product_ids = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    
    context = {
        'new_arrivals': new_arrivals,
        'categories': categories,
        'user_cart_product_ids': user_cart_product_ids,
        'wishlist_product_ids': wishlist_product_ids,
        'testimonials': testimonials,  # Add testimonials to context
    }
    print(f"DEBUG: Context keys: {list(context.keys())}")
    return render(request, 'home.html', context)

# # products/views.py
# def home(request):
#     print("DEBUG: Entering home view")
    
#     new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
#     categories = Category.objects.filter(is_active=True)
    
#     # Fetch all reviews to match shell output
#     # try:
#     #     testimonials = ProductReview.objects.all().order_by('-created_at')[:3]
#     #     print(f"DEBUG: Found {testimonials.count()} testimonials")
#     #     for idx, testimonial in enumerate(testimonials, 1):
#     #         print(f"DEBUG: Testimonial {idx}: user={getattr(testimonial.user, 'username', 'None')}, "
#     #               f"rating={getattr(testimonial, 'rating', 'None')}, "
#     #               f"comment={getattr(testimonial, 'comment', 'None')[:50]}..., "
#     #               f"product={getattr(testimonial.product, 'name', 'None')}")
#     # except Exception as e:
#     #     print(f"DEBUG: Error fetching testimonials: {str(e)}")
#     #     testimonials = []
#     #     messages.error(request, "Failed to load reviews.")
    
#     # # Fallback if no testimonials
#     # if not testimonials:
#     #     total_reviews = ProductReview.objects.count()
#     #     print(f"DEBUG: No testimonials found. Total reviews: {total_reviews}")
#     #     messages.info(request, "No reviews available to display.")
    
#     user_cart_product_ids = []
#     if request.user.is_authenticated:
#         cart = Cart.objects.filter(user=request.user).first()
#         if cart:
#             user_cart_product_ids = list(cart.items.values_list('product_id', flat=True))
    
#     wishlist_product_ids = []
#     if request.user.is_authenticated:
#         wishlist_product_ids = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    
#     context = {
#         'new_arrivals': new_arrivals,
#         'categories': categories,
#         'user_cart_product_ids': user_cart_product_ids,
#         'wishlist_product_ids': wishlist_product_ids,
#         # 'testimonials': testimonials,
#     }
#     print(f"DEBUG: Context keys: {list(context.keys())}")
#     return render(request, 'home.html', context)

# views.py
def about_us(request):
    testimonials = ProductReview.objects.all().order_by('-created_at')[:3]  # Fetch the latest 3 reviews
    print("Testimonials:", testimonials)  # Debug line
    context = {'testimonials': testimonials}
    return render(request, 'aboutus.html', context)

def catalog(request):
    products = Product.objects.filter(is_active=True)
    user_cart_product_ids = []
    cart = get_cart(request)
    if cart:
        user_cart_product_ids = list(cart.items.values_list('product_id', flat=True))

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            user_cart_product_ids = list(cart.items.values_list('product_id', flat=True))

    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        try:
            category_id = int(category_id)
            category = get_object_or_404(Category, id=category_id)
            products = products.filter(category=category)
        except (ValueError, TypeError):
            pass

    # Filter by search query
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price')
    if max_price:
        try:
            max_price = float(max_price)
            # Products with discount_price <= max_price
            products_with_discount = products.filter(
                discount_price__isnull=False,
                discount_price__lte=max_price
            )
            # Products with no discount_price and price <= max_price
            products_without_discount = products.filter(
                discount_price__isnull=True,
                price__lte=max_price
            )
            # Combine both sets
            products = products_with_discount | products_without_discount
        except (ValueError, TypeError):
            pass
    if min_price:
        try:
            min_price = float(min_price)
            # Products with discount_price >= min_price or no discount_price and price >= min_price
            products_with_discount = products.filter(
                discount_price__isnull=False,
                discount_price__gte=min_price
            )
            products_without_discount = products.filter(
                discount_price__isnull=True,
                price__gte=min_price
            )
            products = products_with_discount | products_without_discount
        except (ValueError, TypeError):
            pass

    # Filter by colors
    colors = request.GET.getlist('colors')
    if colors:
        color_queries = [Q(colors__icontains=color) for color in colors]
        color_filter = color_queries.pop()
        for q in color_queries:
            color_filter |= q
        products = products.filter(color_filter)

    # Filter by sizes (single value from dropdown)
    size = request.GET.get('sizes')
    if size:
        products = products.filter(available_sizes__icontains=size)

    # Filter by rating
    rating = request.GET.get('rating')
    if rating:
        try:
            rating = float(rating)
            products = products.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__gte=rating)
        except (ValueError, TypeError):
            pass

    # Filter by availability
    availability = request.GET.get('availability')
    if availability == 'in_stock':
        products = products.filter(stock__gt=0)
    elif availability == 'out_of_stock':
        products = products.filter(stock=0)

   # Sort products
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_asc':
        # Sort by discount_price if available, else price, with id as tiebreaker
        products = products.annotate(
            effective_price=Coalesce('discount_price', 'price')
        ).order_by('effective_price', 'id')
    elif sort_by == 'price_desc':
        products = products.annotate(
            effective_price=Coalesce('discount_price', 'price')
        ).order_by('-effective_price', '-id')
    elif sort_by == 'popular':
        products = products.order_by('-views')
    elif sort_by == 'rating':
        products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating', 'id')
    else:  # newest
        products = products.order_by('-created_at')

    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    # Context data
    categories = Category.objects.filter(is_active=True)
    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist_product_ids = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))

    available_colors = ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'Orange', 'Brown', 'Black', 'White']
    available_sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL']

    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'category_id': category_id,
        'sort_by': sort_by,
        'selected_colors': colors,
        'selected_sizes': [size] if size else [],
        'selected_rating': rating or '',
        'in_stock': availability == 'in_stock',
        'out_of_stock': availability == 'out_of_stock',
        'wishlist_product_ids': wishlist_product_ids,
        'available_colors': available_colors,
        'available_sizes': available_sizes,
        'max_price': max_price,
        'user_cart_product_ids':user_cart_product_ids,
    }

    return render(request, 'products/catalog.html', context)

@property
def avg_rating(self):
    return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    from_param = request.GET.get('from', '')
    # Validate allowed values to prevent unexpected inputs
    allowed_sources = ['profile_wishlist', 'wishlist', 'cart']
    from_source = from_param if from_param in allowed_sources else ''
    
    user_cart_product_ids = []
    cart_item = None
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            user_cart_product_ids = list(cart.items.values_list('product_id', flat=True))
            cart_item = CartItemNew.objects.filter(cart=cart, product=product).first()

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
        'cart_item': cart_item,
        'from_source' : from_source
    }

    return render(request, 'products/detail.html', context)


def category_products(request, category_id):
    """
    View to display products in a specific category
    """
    category = get_object_or_404(Category, id=category_id, is_active=True)

    # Add category to request.GET for filtering in catalog view
    request.GET = request.GET.copy()
    request.GET['category'] = category.id

    return catalog(request)


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f"{product.name} added to wishlist" if created else f"{product.name} already in wishlist",
        })
    return redirect(request.META.get('HTTP_REFERER', '/products/'))



@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        wishlist_item = Wishlist.objects.get(user=request.user, product=product)
        wishlist_item.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f"{product.name} removed from wishlist"})
    except Wishlist.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': f"{product.name} not in wishlist"})
    return redirect(request.META.get('HTTP_REFERER', '/products/'))
    
# products/views.py
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        title = request.POST.get('title')
        comment = request.POST.get('comment')

        # Validate inputs
        if not all([rating, title, comment]):
            messages.error(request, "Please fill all fields to submit a review.")
            return redirect('products:detail', product_id=product_id)

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except ValueError:
            messages.error(request, "Please provide a valid rating between 1 and 5.")
            return redirect('products:detail', product_id=product_id)

        # Check if user already reviewed this product
        existing_review = ProductReview.objects.filter(product=product, user=request.user).first()

        if existing_review:
            # Update existing review
            existing_review.rating = rating
            existing_review.title = title
            existing_review.comment = comment
            existing_review.save()
            messages.success(request, "Your review has been updated.")
        else:
            # Create new review
            ProductReview.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                title=title,
                comment=comment
            )
            messages.success(request, "Your review has been submitted.")

        return redirect('products:detail', product_id=product_id)

    return redirect('products:detail', product_id=product_id)

def search(request):
    """
    View to search for products
    """
    query = request.GET.get('q', '')

    if query:
        # Add search query to request.GET for filtering in catalog view
        request.GET = request.GET.copy()
        request.GET['search'] = query

    return catalog(request)


# def product_detail_api(request, slug):
#     """
#     API endpoint to get product details in JSON format
#     """
#     try:
#         product = get_object_or_404(Product, slug=slug, is_active=True)
        
#         # Get the first image or None
#         image = product.images.first() if hasattr(product, 'images') and product.images.exists() else None
#         image_url = image.image.url if image and image.image else None

#         # Count reviews
#         reviews = product.reviews.all() if hasattr(product, 'reviews') else []
#         review_count = len(reviews)

#         # Calculate average rating
#         if review_count > 0:
#             avg_rating = sum(review.rating for review in reviews) / review_count
#         else:
#             avg_rating = 0

#         # Prepare response data
#         data = {
#             'id': product.id,
#             'name': product.name,
#             'description': product.description,
#             'price': float(product.price),
#             'discount_price': float(product.discount_price) if product.discount_price else None,
#             'in_stock': product.in_stock,
#             'image_url': image_url,
#             'review_count': review_count,
#             'avg_rating': avg_rating,
#             'in_cart' : in_cart,
#             'category': product.category.name if product.category else None,
#         }

#         return JsonResponse(data)
#     except Exception as e:
#         # Log the error and return a 404 response
#         print(f"Error fetching product details: {str(e)}")
#         return JsonResponse({'error': 'Product not found'}, status=404)

          
