from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.catalog, name='catalog'),
    path('product/<int:product_id>/', views.product_detail, name='detail'),
    # path('products/product/<slug:slug>/', views.product_detail, name='detail'),
    path('category/<int:category_id>/', views.category_products, name='category'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('search/', views.product_search, name='product_search'),
    # path('', views.home, name='product_detail'),
    path('product/<int:product_id>/add-review/', views.add_review, name='add_review'),

    # API endpoints
    # path('api/detail/<int:product_id>/', views.product_detail_api, name='product_detail_api'),
]