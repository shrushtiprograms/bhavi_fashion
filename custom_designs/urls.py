from django.urls import path
from . import views

app_name = 'custom_designs'

urlpatterns = [
    path('', views.custom_design_form, name='form'),
    path('submit/', views.submit_custom_design, name='submit'),
    path('details/<int:design_id>/', views.custom_design_details, name='details'),
    path('size-chart/<str:design_type>/', views.get_size_chart, name='size_chart'),
    path('design/<int:design_id>/pay/', views.initiate_payment, name='initiate_payment'),
    path('design/<int:design_id>/success/', views.payment_success, name='payment_success'),
    path('webhook/payment/', views.payment_webhook, name='payment_webhook'),
]