from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart, name='cart'),
    path('order/track/', views.track_order, name='track_order'),
    path('checkout/', views.checkout, name='checkout'),
    path('products/<int:product_id>/', views.product_detail, name='detail'),
    # path('get_cart_item/<int:product_id>/',views.get_cart_item,name="get_cart_item"),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart-quantity/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('history/', views.order_history, name='order_history'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),

     # Payment URLs
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('payment/success/<str:order_number>/', views.payment_success, name='payment_success'),
    path('payment/failure/<str:order_number>/', views.payment_failure, name='payment_failure'),

]