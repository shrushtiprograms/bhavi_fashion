from django.urls import path
from . import views

app_name = 'bulk_orders'

urlpatterns = [
    path('form/', views.bulk_order_form, name='form'),
    path('submit/', views.submit_bulk_order, name='submit'),
    path('details/<int:order_id>/', views.bulk_order_details, name='details'),
    path('initiate-payment/<int:order_id>/', views.initiate_payment, name='initiate_payment'),
    path('payment-success/<int:order_id>/', views.payment_success, name='payment_success'),
]