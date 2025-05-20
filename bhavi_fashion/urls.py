import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from products.models import Product, Category,ProductReview


def home(request):
    """
    Home page view with dynamic content from database
    """
    # Get all active categories
    categories = Category.objects.filter(is_active=True)[:4]
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
    
    # Get new arrivals (latest products added to the store)
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    
    # Get featured products
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:4]
    
    # Fallback if no testimonials
    if not testimonials:
        total_reviews = ProductReview.objects.count()
        print(f"DEBUG: No testimonials found. Total reviews: {total_reviews}")
        
    # Get new arrivals (latest products added to the store)
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:8]

    # Get featured products
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:4]

    context = {
        'categories': categories,
        'new_arrivals': new_arrivals,
        'featured_products': featured_products,
        'testimonials': testimonials,
    }

    return render(request, 'home.html', context)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-dashboard/', include('admin_dashboard.urls')),
    path('', home, name='home'),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),
    path('custom-designs/', include('custom_designs.urls')),
    path('bulk-orders/', include('bulk_orders.urls')),
    path('tailor-jobs/', include('tailor_jobs.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
