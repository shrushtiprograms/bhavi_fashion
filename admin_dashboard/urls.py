from django.urls import path
from . import views
from .views import report_list
app_name = 'admin_dashboard'

urlpatterns = [
    path('login/', views.admin_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/', views.products, name='products'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('categories/', views.categories, name='categories'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('orders/', views.orders, name='orders'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
    path('orders/update-status/<str:order_number>/', views.update_order_status, name='update_order_status'),
    path('custom-designs/', views.custom_designs, name='custom_designs'),
    path('custom-designs/<int:design_id>/', views.custom_design_detail, name='custom_design_detail'),
    path('custom-designs/update-status/<int:design_id>/', views.update_custom_design_status, name='update_custom_design_status'),
    path('bulk-orders/', views.bulk_orders, name='bulk_orders'),
    path('bulk-orders/<int:order_id>/', views.bulk_order_detail, name='bulk_order_detail'),
    path('bulk-orders/update-status/<int:order_id>/', views.update_bulk_order_status, name='update_bulk_order_status'),
    path('tailor-applications/', views.tailor_applications, name='tailor_applications'),
    path('tailor-applications/<int:application_id>/', views.tailor_application_detail, name='tailor_application_detail'),
    path('tailor-applications/update-status/<int:application_id>/', views.update_tailor_application_status, name='update_tailor_application_status'),
    path('admin/reports/', report_list, name='report_list'),  
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/inventory/', views.inventory_report, name='inventory_report'),
    path('reports/customers/', views.customer_report, name='customer_report'),
    path('wishlist-overview/', views.wishlist_overview, name='wishlist_overview'),
    path('cart-overview/', views.cart_overview, name='cart_overview'),
]
