import os
import sys
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import connection

# Setup Django environment first
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if not settings.configured:
    print(f"Current DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    try:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'bhavi_fashion.settings'
        import django
        django.setup()
        print("Successfully configured settings via environment.")
    except ImproperlyConfigured as e:
        print(f"Environment setup failed: {e}. Using manual configuration.")
        import django
        settings.configure(
            DEBUG=True,
            LLOWED_HOSTS=['localhost', '127.0.0.1', 'testserver'], 
            INSTALLED_APPS=[
                'jazzmin',
                'django.contrib.admin',
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.messages',
                'django.contrib.staticfiles',
                'bhavi_fashion',
                'accounts',
                'orders',
                'custom_designs',
                'bulk_orders',
                'tailor_jobs',
                'admin_dashboard',
                'virtual_tryon',
                'products.apps.ProductsConfig',
                'report_manager',
            ],
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.mysql',
                    'NAME': os.environ.get('DB_NAME', 'bhavi_india_fashion'),
                    'USER': os.environ.get('DB_USER', 'Srushti'),
                    'PASSWORD': os.environ.get('DB_PASSWORD', 'shrushti@0227'),
                    'HOST': os.environ.get('DB_HOST', 'localhost'),
                    'PORT': os.environ.get('DB_PORT', '3307'),
                }
            },
            TIME_ZONE='Asia/Kolkata',
            USE_TZ=True,
            ROOT_URLCONF='bhavi_fashion.urls',
            STATIC_URL='/static/',
            MEDIA_URL='/media/',
            AUTH_USER_MODEL='accounts.User',
        )
        django.setup()
        print("Manual configuration applied.")
else:
    print("Settings already configured.")

# Import Django modules after setup
from django.test import Client
from django.urls import reverse
from accounts.models import User  # Using custom User model
from tailor_jobs.models import TailorApplication
from products.models import Product, Category  # Added Category import
from orders.models import Order, OrderItem
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

class TestCaseVerifier:
    def __init__(self):
        self.client = Client()
        self.setup_test_data()

    def setup_test_data(self):
        # Clear existing test data first
        User.objects.filter(username__in=['user@example.com', 'admin@example.com']).delete()
        Product.objects.all().delete()
        Order.objects.all().delete()
        OrderItem.objects.all().delete()
        TailorApplication.objects.all().delete()
        Category.objects.all().delete()

        # 1. First create categories
        self.kurta_category = Category.objects.create(name='Kurta')
        self.pant_category = Category.objects.create(name='Pant')
        self.kurti_category = Category.objects.create(name='Kurti')
        self.choli_category = Category.objects.create(name='Choli')

        # 2. Then create users
        self.user = User.objects.create_user(
            username='user@example.com',
            email='user@example.com',
            password='user@123'
        )
        self.admin = User.objects.create_user(
            username='admin@example.com',
            email='admin@example.com',
            password='admin@123',
            is_staff=True,
            is_superuser=True
        )

        # 3. Now create products (which need categories)
        self.product = Product.objects.create(
            name='Silk Kurta',
            price=3000,
            category=self.kurta_category
        )

        # 4. Create orders (which need users)
        self.order = Order.objects.create(user=self.user)

        # 5. Create order items (which need orders and products)
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=self.product.price  # Make sure to set price
        )

        # 6. Create tailor applications
        self.tailor_app = TailorApplication.objects.create(
            user=self.user,
            name='Test Tailor',
            phone='1234567890',
            address='Test Address'
        )
    def run_test_case(self, test_case_id, description, test_function, expected_result, input_data=None):
        print(f"\nTest Case {test_case_id}: {description}")
        actual_result = test_function(input_data) if input_data else test_function()
        print(f"Expected Result: {expected_result}")
        print(f"Actual Result: {actual_result}")
        print("-" * 50)
        return actual_result == expected_result

    # User Authentication Test Cases (TC001-TC013)
    def test_tc001_registration_success(self, input_data=None):
        response = self.client.post(reverse('accounts:register'), {
            'name': 'user01', 'email': 'user01@test.com', 'contact': '1234567890',
            'password1': 'Test@123', 'password2': 'Test@123'
        }, follow=True)
        return response.status_code == 200 and User.objects.filter(email='user01@test.com').exists()

    def test_tc002_registration_password_mismatch(self, input_data=None):
        response = self.client.post(reverse('accounts:register'), {
            'name': 'user02', 'email': 'user02@test.com', 'contact': '1234567890',
            'password1': 'Test@123', 'password2': 'Wrong123'
        })
        return 'Passwords do not match' in str(response.content)

    def test_tc003_registration_existing_email(self, input_data=None):
        response = self.client.post(reverse('accounts:register'), {
            'name': 'user03', 'email': 'user@example.com', 'contact': '1234567890',
            'password1': 'Test@123', 'password2': 'Test@123'
        })
        return 'Email already registered' in str(response.content)

    def test_tc004_registration_invalid_contact(self, input_data=None):
        response = self.client.post(reverse('accounts:register'), {
            'name': 'user04', 'email': 'user04@test.com', 'contact': 'abc123',
            'password1': 'Test@123', 'password2': 'Test@123'
        })
        return 'Enter a valid phone number' in str(response.content)

    def test_tc005_password_visibility(self, input_data=None):
        response = self.client.get(reverse('accounts:login'))
        return 'type="password"' in str(response.content)

    def test_tc006_login_admin_success(self, input_data=None):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'admin@example.com', 'password': 'admin@123'
        }, follow=True)
        return response.status_code == 200 and '/admin/' in response.url

    def test_tc007_login_user_success(self, input_data=None):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'user@example.com', 'password': 'user@123'
        }, follow=True)
        return response.status_code == 200 and '/home/' in response.url

    def test_tc008_login_invalid_password(self, input_data=None):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'user@example.com', 'password': 'wrongpass'
        })
        return 'Invalid password' in str(response.content)

    def test_tc009_login_non_existing_user(self, input_data=None):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'unknown@example.com', 'password': 'anyvalue'
        })
        return 'User not found' in str(response.content)

    def test_tc010_login_password_visibility(self, input_data=None):
        response = self.client.get(reverse('accounts:login'))
        return 'type="password"' in str(response.content)

    def test_tc011_forgot_password(self, input_data=None):
        response = self.client.get(reverse('accounts:login'))
        return 'Forgot password?' in str(response.content) and reverse('password_reset') in str(response.content)

    def test_tc012_login_empty_fields(self, input_data=None):
        response = self.client.post(reverse('accounts:login'), {'username': '', 'password': ''})
        return 'This field is required' in str(response.content)

    def test_tc013_register_link(self, input_data=None):
        response = self.client.get(reverse('accounts:login'))
        return 'Register' in str(response.content) and reverse('accounts:register') in str(response.content)

    # Product Catalog Test Cases (TC014-TC017)
    def test_tc014_product_listing(self, input_data=None):
        response = self.client.get(reverse('products:category'))
        return response.status_code == 200 and 'Silk Kurta' in str(response.content)

    def test_tc015_product_filtering(self, input_data=None):
        response = self.client.get(reverse('products:category') + '?category=Kurta')
        return response.status_code == 200 and 'Silk Kurta' in str(response.content)

    def test_tc016_product_search(self, input_data=None):
        response = self.client.get(reverse('products:category') + '?q=Silk')
        return response.status_code == 200 and 'Silk Kurta' in str(response.content)

    def test_tc017_product_details(self, input_data=None):
        response = self.client.get(reverse('products:category', kwargs={'pk': self.product.id}))
        return response.status_code == 200 and 'Silk Kurta' in str(response.content)

    # Shopping Cart & Checkout (TC018-TC020)
    def test_tc018_add_to_cart(self, input_data=None):
        self.client.login(email='user@example.com', password='user@123')
        response = self.client.post(reverse('cart:add', kwargs={'product_id': self.product.id}))
        cart = self.client.session.get('cart', {})
        return response.status_code == 200 and str(self.product.id) in cart

    def test_tc019_checkout_process(self, input_data=None):
        self.client.login(email='user@example.com', password='user@123')
        response = self.client.post(reverse('orders:checkout'), {'payment_method': 'card'}, follow=True)
        return 'Order confirmation' in str(response.content)

    def test_tc020_cart_update(self, input_data=None):
        self.client.login(email='user@example.com', password='user@123')
        response = self.client.post(reverse('cart:update', kwargs={'product_id': self.product.id}), {'quantity': 3})
        cart = self.client.session.get('cart', {})
        return cart.get(str(self.product.id), {}).get('quantity', 0) == 3

    # Bulk Order Test Cases (TC021-TC025)
    def test_tc021_bulk_order_form(self, input_data=None):
        self.client.login(email='user@example.com', password='user@123')
        response = self.client.get(reverse('bulk_orders:form'))
        return response.status_code == 200

    def test_tc022_product_selection(self, input_data=None):
        self.client.login(email='user@example.com', password='user@123')
        response = self.client.post(reverse('bulk_orders:add_product'), {'product_id': self.product.id})
        return 'Silk Kurta' in str(response.content)

    def test_tc023_custom_design(self, input_data=None):
        self.client.login(email='user@example.com', password='user@123')
        with open('test_design.jpg', 'rb') as fp:
            response = self.client.post(reverse('bulk_orders:add_design'), {'design': fp})
        return response.status_code == 200

    def test_tc024_minimum_quantity(self, input_data=None):
        self.client.login(email='user@example.com', password='user@123')
        response = self.client.post(reverse('bulk_orders:submit'), {'quantity': 5})
        return 'Minimum 10 pieces' in str(response.content)

    def test_tc025_bulk_submission(self, input_data=None):
        self.client.login(email='user@example.com', password='user@123')
        with open('test_design.jpg', 'rb') as fp:
            response = self.client.post(reverse('bulk_orders:submit'), {
                'product_id': self.product.id, 'quantity': 10, 'design': fp
            }, follow=True)
        return 'Order confirmation' in str(response.content)

    # Customization Test Cases (TC026-TC028)
    def test_tc026_design_upload(self, input_data=None):
        self.client.login(email='user@example.com', password='user@123')
        with open('test_design.jpg', 'rb') as fp:
            response = self.client.post(reverse('custom_designs:upload'), {'design': fp})
        return response.status_code == 200

    def test_tc027_invalid_file_type(self, input_data=None):
        self.client.login(email='user@example.com', password='user@123')
        with open('test_design.pdf', 'rb') as fp:
            response = self.client.post(reverse('custom_designs:upload'), {'design': fp})
        return 'Invalid format' in str(response.content)

    def test_tc028_color_selection(self, input_data=None):
        self.client.login(email='user@example.com', password='user@123')
        response = self.client.post(reverse('custom_designs:select_color'), {'color': 'Red'})
        return 'Red' in str(response.content)

    # Tailor Job Application (TC029-TC032)
    def test_tc029_application_form(self, input_data=None):
        response = self.client.get(reverse('tailor_jobs:form'))
        return response.status_code == 200

    def test_tc030_resume_upload(self, input_data=None):
        self.client.login(email='user@example.com', password='user@123')
        with open('resume.pdf', 'rb') as fp:
            response = self.client.post(reverse('tailor_jobs:apply'), {'resume': fp}, follow=True)
        return 'Application submitted' in str(response.content)

    def test_tc031_portfolio_upload(self, input_data=None):
        self.client.login(email='user@example.com', password='user@123')
        with open('portfolio.jpg', 'rb') as fp:
            response = self.client.post(reverse('tailor_jobs:apply'), {'portfolio': fp}, follow=True)
        return 'Preview available' in str(response.content)

    def test_tc032_form_submission(self, input_data=None):
        self.client.login(email='user@example.com', password='user@123')
        with open('portfolio.jpg', 'rb') as fp:
            response = self.client.post(reverse('tailor_jobs:apply'), {
                'name': 'Test Tailor', 'phone': '1234567890', 'address': 'Test Address',
                'experience': '1-2 years', 'skills': 'Kurti', 'work_mode': 'Work from Home', 'sample_work': fp
            }, follow=True)
        return 'Confirmation email sent' in str(response.content)

    # Admin Panel Test Cases (TC033-TC035)
    def test_tc033_order_management(self, input_data=None):
        self.client.login(email='admin@example.com', password='admin@123')
        response = self.client.get(reverse('admin:orders_order_changelist'))
        return response.status_code == 200

    def test_tc034_tailor_approval(self, input_data=None):
        self.client.login(email='admin@example.com', password='admin@123')
        self.tailor_app.status = 'pending'
        self.tailor_app.save()
        response = self.client.post(reverse('admin:tailor_jobs_tailorapplication_change', args=[self.tailor_app.id]), {'status': 'approved'})
        return TailorApplication.objects.get(id=self.tailor_app.id).status == 'approved'

    def test_tc035_inventory_update(self, input_data=None):
        self.client.login(email='admin@example.com', password='admin@123')
        response = self.client.post(reverse('admin:products_product_add'), {
            'name': 'New Kurta', 'price': 3000, 'category': self.kurta_category.id
        })
        return 'New Kurta' in str(response.content)

    # Payment Gateway (TC036-TC037)
    def test_tc036_razorpay_success(self, input_data=None):
        self.client.login(email='user@example.com', password='user@123')
        response = self.client.post(reverse('orders:payment'), {'card_number': '4111111111111111'}, follow=True)
        return 'Payment success' in str(response.content)

    def test_tc037_razorpay_failed(self, input_data=None):
        self.client.login(email='user@example.com', password='user@123')
        response = self.client.post(reverse('orders:payment'), {'card_number': '4000000000000002'}, follow=True)
        return 'Error message' in str(response.content)

    # Responsiveness (TC038-TC039)
    def test_tc038_mobile_responsiveness(self, input_data=None):
        response = self.client.get(reverse('products:product_list'))
        return response.status_code == 200  # Manual browser emulation needed

    def test_tc039_tablet_responsiveness(self, input_data=None):
        self.client.login(email='user@example.com', password='user@123')
        response = self.client.get(reverse('orders:checkout'))
        return response.status_code == 200  # Manual browser emulation needed

    # Security (TC040-TC041)
    def test_tc040_sql_injection(self, input_data=None):
        response = self.client.post(reverse('login'), {
            'username': "user@example.com' OR '1'='1", 'password': 'any'
        })
        return 'Invalid password' in str(response.content) and 'SQL error' not in str(response.content)

    def test_tc041_xss_protection(self, input_data=None):
        response = self.client.get(reverse('products:product_list') + '?q=<script>alert(1)</script>')
        return '<script>' not in str(response.content)

    # def verify_all_test_cases(self):
    #     test_cases = [
    #         ('TC001', 'Registration Success', self.test_tc001_registration_success,
    #          'Redirects to login and user created', {'name': 'user01', 'email': 'user01@test.com'}),
    #         ('TC002', 'Registration Password Mismatch', self.test_tc002_registration_password_mismatch,
    #          'Error: Passwords do not match'),
    #         ('TC003', 'Registration Existing Email', self.test_tc003_registration_existing_email,
    #          'Error: Email already registered'),
    #         ('TC004', 'Registration Invalid Contact', self.test_tc004_registration_invalid_contact,
    #          'Validation error'),
    #         ('TC005', 'Password Visibility', self.test_tc005_password_visibility,
    #          'Password field visible'),
    #         ('TC006', 'Login Admin Success', self.test_tc006_login_admin_success,
    #          'Redirect to admin dashboard'),
    #         ('TC007', 'Login User Success', self.test_tc007_login_user_success,
    #          'Redirect to user dashboard'),
    #         ('TC008', 'Login Invalid Password', self.test_tc008_login_invalid_password,
    #          'Error: Invalid password'),
    #         ('TC009', 'Login Non-existing User', self.test_tc009_login_non_existing_user,
    #          'Error: User not found'),
    #         ('TC010', 'Login Password Visibility', self.test_tc010_login_password_visibility,
    #          'Password field visible'),
    #         ('TC011', 'Forgot Password', self.test_tc011_forgot_password,
    #          'Forgot password link and reset page'),
    #         ('TC012', 'Login Empty Fields', self.test_tc012_login_empty_fields,
    #          'Validation error'),
    #         ('TC013', 'Register Link', self.test_tc013_register_link,
    #          'Register link visible'),
    #         ('TC014', 'Product Listing', self.test_tc014_product_listing,
    #          'Products displayed'),
    #         ('TC015', 'Product Filtering', self.test_tc015_product_filtering,
    #          'Filtered products displayed'),
    #         ('TC016', 'Product Search', self.test_tc016_product_search,
    #          'Search results displayed'),
    #         ('TC017', 'Product Details', self.test_tc017_product_details,
    #          'Product details displayed'),
    #         ('TC018', 'Add to Cart', self.test_tc018_add_to_cart,
    #          'Item added to cart'),
    #         ('TC019', 'Checkout Process', self.test_tc019_checkout_process,
    #          'Order confirmation'),
    #         ('TC020', 'Cart Update', self.test_tc020_cart_update,
    #          'Quantity updated'),
    #         ('TC021', 'Bulk Order Form', self.test_tc021_bulk_order_form,
    #          'Form loads'),
    #         ('TC022', 'Product Selection', self.test_tc022_product_selection,
    #          'Product selected'),
    #         ('TC023', 'Custom Design', self.test_tc023_custom_design,
    #          'Design uploaded'),
    #         ('TC024', 'Minimum Quantity', self.test_tc024_minimum_quantity,
    #          'Minimum quantity error'),
    #         ('TC025', 'Bulk Submission', self.test_tc025_bulk_submission,
    #          'Order confirmation'),
    #         ('TC026', 'Design Upload', self.test_tc026_design_upload,
    #          'Design uploaded'),
    #         ('TC027', 'Invalid File Type', self.test_tc027_invalid_file_type,
    #          'Invalid format error'),
    #         ('TC028', 'Color Selection', self.test_tc028_color_selection,
    #          'Color selected'),
    #         ('TC029', 'Application Form', self.test_tc029_application_form,
    #          'Form loads'),
    #         ('TC030', 'Resume Upload', self.test_tc030_resume_upload,
    #          'Application submitted'),
    #         ('TC031', 'Portfolio Upload', self.test_tc031_portfolio_upload,
    #          'Preview available'),
    #         ('TC032', 'Form Submission', self.test_tc032_form_submission,
    #          'Confirmation email sent'),
    #         ('TC033', 'Order Management', self.test_tc033_order_management,
    #          'Orders visible'),
    #         ('TC034', 'Tailor Approval', self.test_tc034_tailor_approval,
    #          'Status approved'),
    #         ('TC035', 'Inventory Update', self.test_tc035_inventory_update,
    #          'New product added'),
    #         ('TC036', 'Razorpay Success', self.test_tc036_razorpay_success,
    #          'Payment success'),
    #         ('TC037', 'Razorpay Failed', self.test_tc037_razorpay_failed,
    #          'Error message'),
    #         ('TC038', 'Mobile Responsiveness', self.test_tc038_mobile_responsiveness,
    #          'Page loads', {'note': 'Manual browser emulation needed'}),
    #         ('TC039', 'Tablet Responsiveness', self.test_tc039_tablet_responsiveness,
    #          'Page loads', {'note': 'Manual browser emulation needed'}),
    #         ('TC040', 'SQL Injection', self.test_tc040_sql_injection,
    #          'Input sanitized'),
    #         ('TC041', 'XSS Protection', self.test_tc041_xss_protection,
    #          'Script tag removed'),
    #     ]
    def verify_all_test_cases(self):
        test_cases = [
            ('TC001', 'Registration Success', self.test_tc001_registration_success,
             'Redirects to login and user created', None),
            ('TC002', 'Registration Password Mismatch', self.test_tc002_registration_password_mismatch,
             'Error: Passwords do not match',None),
            ('TC003', 'Registration Existing Email', self.test_tc003_registration_existing_email,
             'Error: Email already registered',None),
            ('TC004', 'Registration Invalid Contact', self.test_tc004_registration_invalid_contact,
             'Validation error',None),
            ('TC005', 'Password Visibility', self.test_tc005_password_visibility,
             'Password field visible',None),
            ('TC006', 'Login Admin Success', self.test_tc006_login_admin_success,
             'Redirect to admin dashboard',None),
            ('TC007', 'Login User Success', self.test_tc007_login_user_success,
             'Redirect to user dashboard',None),
            ('TC008', 'Login Invalid Password', self.test_tc008_login_invalid_password,
             'Error: Invalid password',None),
            ('TC009', 'Login Non-existing User', self.test_tc009_login_non_existing_user,
             'Error: User not found',None),
            ('TC010', 'Login Password Visibility', self.test_tc010_login_password_visibility,
             'Password field visible',None),
            ('TC011', 'Forgot Password', self.test_tc011_forgot_password,
             'Forgot password link and reset page',None),
            ('TC012', 'Login Empty Fields', self.test_tc012_login_empty_fields,
             'Validation error',None),
            ('TC013', 'Register Link', self.test_tc013_register_link,
             'Register link visible',None),
            ('TC014', 'Product Listing', self.test_tc014_product_listing,
             'Products displayed',None),
            ('TC015', 'Product Filtering', self.test_tc015_product_filtering,
             'Filtered products displayed',None),
            ('TC016', 'Product Search', self.test_tc016_product_search,
             'Search results displayed',None),
            ('TC017', 'Product Details', self.test_tc017_product_details,
             'Product details displayed',None),
            ('TC018', 'Add to Cart', self.test_tc018_add_to_cart,
             'Item added to cart',None),
            ('TC019', 'Checkout Process', self.test_tc019_checkout_process,
             'Order confirmation',None),
            ('TC020', 'Cart Update', self.test_tc020_cart_update,
             'Quantity updated',None),
            ('TC021', 'Bulk Order Form', self.test_tc021_bulk_order_form,
             'Form loads',None),
            ('TC022', 'Product Selection', self.test_tc022_product_selection,
             'Product selected',None),
            ('TC023', 'Custom Design', self.test_tc023_custom_design,
             'Design uploaded',None),
            ('TC024', 'Minimum Quantity', self.test_tc024_minimum_quantity,
             'Minimum quantity error',None),
            ('TC025', 'Bulk Submission', self.test_tc025_bulk_submission,
             'Order confirmation',None),
            ('TC026', 'Design Upload', self.test_tc026_design_upload,
             'Design uploaded',None),
            ('TC027', 'Invalid File Type', self.test_tc027_invalid_file_type,
             'Invalid format error',None),
            ('TC028', 'Color Selection', self.test_tc028_color_selection,
             'Color selected',None),
            ('TC029', 'Application Form', self.test_tc029_application_form,
             'Form loads',None),
            ('TC030', 'Resume Upload', self.test_tc030_resume_upload,
             'Application submitted',None),
            ('TC031', 'Portfolio Upload', self.test_tc031_portfolio_upload,
             'Preview available',None),
            ('TC032', 'Form Submission', self.test_tc032_form_submission,
             'Confirmation email sent',None),
            ('TC033', 'Order Management', self.test_tc033_order_management,
             'Orders visible',None),
            ('TC034', 'Tailor Approval', self.test_tc034_tailor_approval,
             'Status approved',None),
            ('TC035', 'Inventory Update', self.test_tc035_inventory_update,
             'New product added',None),
            ('TC036', 'Razorpay Success', self.test_tc036_razorpay_success,
             'Payment success',None),
            ('TC037', 'Razorpay Failed', self.test_tc037_razorpay_failed,
             'Error message',None),
            ('TC038', 'Mobile Responsiveness', self.test_tc038_mobile_responsiveness,
             'Page loads', None),
            ('TC039', 'Tablet Responsiveness', self.test_tc039_tablet_responsiveness,
             'Page loads', None),
            ('TC040', 'SQL Injection', self.test_tc040_sql_injection,
             'Input sanitized',None),
            ('TC041', 'XSS Protection', self.test_tc041_xss_protection,
             'Script tag removed',None),
        ]
        all_passed = True
        for test_case_id, description, test_func, expected, input_data in test_cases:
            passed = self.run_test_case(test_case_id, description, test_func, expected, input_data)
            if not passed and 'note' not in (input_data or {}):
                all_passed = False
        return all_passed

def generate_pdf_report(passed_tests):
    """Generate a PDF report of all test cases with results."""
    pdf_file = 'test_cases_report.pdf'
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("BHAVI FASHION TEST CASES REPORT", styles['Title']))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))

    test_cases = [
        ['TC001', 'Registration', 'Successful registration', 'Fill all fields correctly', 'Name: user01, Email: user01@test.com', 'Redirects to login' if passed_tests else 'Failed'],
        ['TC002', 'Registration', 'Passwords do not match', 'Enter mismatching passwords', 'Password: Test@123, Confirm: Wrong123', 'Error: Passwords do not match' if passed_tests else 'Failed'],
        ['TC003', 'Registration', 'Existing username or email', 'Use existing email', 'Email: user@example.com', 'Error: Email already registered' if passed_tests else 'Failed'],
        ['TC004', 'Registration', 'Invalid contact number', 'Enter non-numeric contact', 'Contact: abc123', 'Validation error' if passed_tests else 'Failed'],
        ['TC005', 'Password Visibility', 'Toggle password visibility', 'Click eye icon', 'N/A', 'Password field visible' if passed_tests else 'Failed'],
        ['TC006', 'Login Form', 'Successful admin login', 'Enter valid admin credentials', 'Email: admin@example.com', 'Redirect to admin dashboard' if passed_tests else 'Failed'],
        ['TC007', 'Login Form', 'Successful user login', 'Enter valid user credentials', 'Email: user@example.com', 'Redirect to user dashboard' if passed_tests else 'Failed'],
        ['TC008', 'Login Form', 'Incorrect password', 'Enter valid email with wrong password', 'Password: wrongpass', 'Error: Invalid password' if passed_tests else 'Failed'],
        ['TC009', 'Login Form', 'Non-existing user', 'Enter unregistered email', 'Email: unknown@example.com', 'Error: User not found' if passed_tests else 'Failed'],
        ['TC010', 'Login Form', 'Password visibility toggle', 'Click eye icon', 'N/A', 'Password field visible' if passed_tests else 'Failed'],
        ['TC011', 'Forgot Password', 'Forgot password link', 'Click "Forgot Password?"', 'N/A', 'Forgot password link and reset page' if passed_tests else 'Failed'],
        ['TC012', 'Login Form', 'Empty fields', 'Submit with empty fields', 'Email/Password: empty', 'Validation error' if passed_tests else 'Failed'],
        ['TC013', 'Register Link', 'Register link navigation', 'Click "Register here"', 'N/A', 'Register link visible' if passed_tests else 'Failed'],
        ['TC014', 'Product Listing', 'View all products', 'Load products page', 'N/A', 'Products displayed' if passed_tests else 'Failed'],
        ['TC015', 'Product Filtering', 'Filter by category', 'Select "Kurta"', 'Category: Kurta', 'Filtered products displayed' if passed_tests else 'Failed'],
        ['TC016', 'Product Search', 'Search functionality', 'Enter "Silk"', 'Query: Silk', 'Search results displayed' if passed_tests else 'Failed'],
        ['TC017', 'Product Details', 'View product details', 'Click product', 'Product ID: 101', 'Product details displayed' if passed_tests else 'Failed'],
        ['TC018', 'Add to Cart', 'Single product', 'Click "Add to Cart"', 'Product ID: 102', 'Item added to cart' if passed_tests else 'Failed'],
        ['TC019', 'Checkout Process', 'Complete purchase', 'Proceed through checkout', 'Valid payment details', 'Order confirmation' if passed_tests else 'Failed'],
        ['TC020', 'Cart Update', 'Modify quantity', 'Change quantity to 3', 'Qty: 3', 'Quantity updated' if passed_tests else 'Failed'],
        ['TC021', 'Bulk Order Form', 'Access form', 'Click "Bulk Orders"', 'N/A', 'Form loads' if passed_tests else 'Failed'],
        ['TC022', 'Product Selection', 'Add existing product', 'Select from dropdown', 'Product: Silk Kurta', 'Product selected' if passed_tests else 'Failed'],
        ['TC023', 'Custom Design', 'Upload design', 'Upload 3 images', '3 image files', 'Design uploaded' if passed_tests else 'Failed'],
        ['TC024', 'Minimum Quantity', 'Below minimum qty', 'Enter qty: 5', 'Qty: 5', 'Minimum quantity error' if passed_tests else 'Failed'],
        ['TC025', 'Bulk Submission', 'Submit complete form', 'Fill all fields', 'Valid business details', 'Order confirmation' if passed_tests else 'Failed'],
        ['TC026', 'Design Upload', 'Valid design files', 'Upload JPG/PNG', '2MB image', 'Design uploaded' if passed_tests else 'Failed'],
        ['TC027', 'Invalid File Type', 'Upload PDF', 'Upload design.pdf', 'PDF file', 'Invalid format error' if passed_tests else 'Failed'],
        ['TC028', 'Color Selection', 'Choose color', 'Select Red', 'Color: Red', 'Color selected' if passed_tests else 'Failed'],
        ['TC029', 'Application Form', 'Access form', 'Click "Become a Tailor"', 'N/A', 'Form loads' if passed_tests else 'Failed'],
        ['TC030', 'Resume Upload', 'Valid resume', 'Upload PDF', 'resume.pdf', 'Application submitted' if passed_tests else 'Failed'],
        ['TC031', 'Portfolio Upload', 'Image samples', 'Upload 3 images', 'JPG files', 'Preview available' if passed_tests else 'Failed'],
        ['TC032', 'Form Submission', 'Complete application', 'Fill all fields', 'Valid experience', 'Confirmation email sent' if passed_tests else 'Failed'],
        ['TC033', 'Order Management', 'View bulk orders', 'Login as admin', 'Admin credentials', 'Orders visible' if passed_tests else 'Failed'],
        ['TC034', 'Tailor Approval', 'Approve applicant', 'Review application', 'Applicant ID: TAIL202', 'Status approved' if passed_tests else 'Failed'],
        ['TC035', 'Inventory Update', 'Add new product', 'Fill product form', 'New product details', 'New product added' if passed_tests else 'Failed'],
        ['TC036', 'Razorpay Integration', 'Successful payment', 'Complete checkout', 'Test card details', 'Payment success' if passed_tests else 'Failed'],
        ['TC037', 'Failed Payment', 'Declined card', 'Enter invalid card', 'Card: 4111...', 'Error message' if passed_tests else 'Failed'],
        ['TC038', 'Mobile', 'Product page', 'View on 360px width', 'N/A', 'Page loads' if passed_tests else 'Failed'],
        ['TC039', 'Tablet', 'Checkout process', 'Complete on iPad', 'N/A', 'Page loads' if passed_tests else 'Failed'],
        ['TC040', 'SQL Injection', 'Login form', 'Enter SQL in email', 'N/A', 'Input sanitized' if passed_tests else 'Failed'],
        ['TC041', 'XSS Protection', 'Search field', 'Enter script tag', 'N/A', 'Script tag removed' if passed_tests else 'Failed'],
    ]

    table = Table(test_cases)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)
    print(f"PDF report generated: {pdf_file}")

if __name__ == '__main__':
    verifier = TestCaseVerifier()
    all_passed = verifier.verify_all_test_cases()
    generate_pdf_report(all_passed)# Import Django modules after setup
