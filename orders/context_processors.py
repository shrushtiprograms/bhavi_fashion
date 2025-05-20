from .models import CartItemNew


def cart_processor(request):
    """
    Context processor to add cart count and items to all templates
    """
    cart_count = 0
    cart_total = 0

    if request.user.is_authenticated:
        cart_items = CartItemNew.objects.filter(cart__user=request.user)
        cart_count = sum(item.quantity for item in cart_items)
        cart_total = sum(item.product.current_price * item.quantity for item in cart_items)

    return {
        'cart_count': cart_count,
        'cart_total': cart_total
    }