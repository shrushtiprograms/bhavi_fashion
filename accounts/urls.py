from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('view-site-as-user/', views.view_site_as_user, name='view_site_as_user'),
    path('logout/', views.logout_view, name='logout'),
    path('wishlist/remove/<int:wishlist_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('profile/', views.profile_view, name='profile'),
    path('about/', views.about, name='about'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/addresses/', views.address_list, name='address_list'),
    path('contact/submit/', views.contact_submit, name='contact_submit'),
    path('customer/support/', views.support, name='support'),
    path('contact_us/', views.contact_view, name='contact_us'),
    path('address/set-default/<int:address_id>/', views.set_default_address, name='set_default_address'),
    path('profile/addresses/add/', views.add_address, name='add_address'),
    path('profile/addresses/edit/<int:pk>/', views.edit_address, name='edit_address'),
    path('profile/addresses/delete/<int:pk>/', views.delete_address, name='delete_address'),
    path('profile/orders/', views.order_history, name='order_history'),
    path('profile/wishlist/', views.wishlist, name='wishlist'),
    # Add clear wishlist URL
    path('profile/wishlist/clear/', views.clear_wishlist, name='clear_wishlist'),
    path('profile/custom-designs/', views.custom_designs, name='custom_designs'),
    path('profile/bulk-orders/', views.bulk_orders, name='bulk_orders'),
    path('debug-urls/', views.debug_urls, name='debug_urls'),
    # Password reset URLs
    path('password_reset/', views.forgot_password, name='password_reset'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('return-policy/', views.return_policy, name='return_policy'),
]
