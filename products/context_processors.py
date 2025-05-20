from .models import Wishlist, Product, Category


def wishlist_count(request):
    """
    Context processor to make wishlist count available across all templates
    """
    count = 0
    wishlist_items = []

    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user)
        count = wishlist_items.count()

    # Create a list of product IDs in the wishlist for easy checking in templates
    wishlist_product_ids = [item.product.id for item in wishlist_items]

    return {
        'wishlist_count': count,
        'wishlist_product_ids': wishlist_product_ids
    }


def categories_processor(request):
    """
    Context processor to make categories available across all templates
    """
    categories = Category.objects.filter(is_active=True)

    return {
        'all_categories': categories,
    }


def featured_products_processor(request):
    """
    Context processor to make featured products available across all templates
    """
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]

    return {
        'featured_products': featured_products,
    }