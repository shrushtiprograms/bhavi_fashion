import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-bhavi-fashion-dev-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Project apps
    'bhavi_fashion',
    'accounts',
    'orders',
    'custom_designs',
    'bulk_orders',
    'tailor_jobs',
    'admin_dashboard',
    'products.apps.ProductsConfig',
    'report_manager',

]

JAZZMIN_SETTINGS = {
    "theme": "slate",
    # Branding
    "site_title": "Bhavi India Fashion Admin",
    "site_header": "Bhavi India",
    "site_brand": "Bhavi India",
    # "site_logo": "static/images/logo.jpg",  # Place logo in static/images/
    "welcome_sign": "Welcome to Bhavi India Admin",
    "copyright": "Bhavi India Fashion Ltd",

    # UI Customization
    "show_sidebar": True,              # Display sidebar
    "navigation_expanded": False,      # Sidebar collapsed by default
    "hide_apps": [],                   # Apps to hide from sidebar
    "hide_models": [],                 # Models to hide
    "custom_css": "css/custom.css",    # Path to custom CSS in static folder
    "custom_js": None,                 # Optional custom JS

    # Icons (Font Awesome classes)
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "accounts.User": "fas fa-user",
        "accounts.Address": "fas fa-map-marker-alt",
        "bulk_orders.BulkOrder": "fas fa-truck",
        "custom_designs.CustomDesign": "fas fa-paint-brush",
        "orders.Order": "fas fa-shopping-cart",
        "orders.Cart": "fas fa-cart-plus",
        "products.Product": "fas fa-box",
        "products.Category": "fas fa-tags",
        "tailor_jobs.TailorApplication": "fas fa-users",
    },

    # Top Menu Links
    "topmenu_links": [
        {"name": "View Site", "url": "/", "new_window": True},
    ],

    # User Menu Links (top-right dropdown)
    "usermenu_links": [
        {"name": "Profile", "url": "accounts:profile", "icon": "fas fa-user"},
        {"name": "Logout", "url": "accounts:logout", "icon": "fas fa-sign-out-alt"},
    ],

    # Change Form Layout
    "changeform_format": "horizontal_tabs",  # Options: "horizontal_tabs", "vertical_tabs", "collapsible", "carousel"
}
JAZZMIN_SETTINGS["hide_apps"] = ["auth"]  # Hides default auth app
JAZZMIN_SETTINGS["hide_models"] = ["auth.Group"]  # Hides specific models
JAZZMIN_SETTINGS["related_modal_active"] = True
JAZZMIN_SETTINGS["show_ui_builder"] = True
JAZZMIN_SETTINGS["changeform_format_overrides"] = {
    "accounts.User": "vertical_tabs",
    "products.Product": "collapsible",
}
JAZZMIN_SETTINGS["show_ui_builder"] = True


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bhavi_fashion.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'products.context_processors.categories_processor',
                'products.context_processors.featured_products_processor',
                'products.context_processors.wishlist_count',
                'orders.context_processors.cart_processor',
            ],
            'debug': DEBUG,
        },
    },
]

WSGI_APPLICATION = 'bhavi_fashion.wsgi.application'
SHIPROCKET_TOKEN = 'your_shiprocket_token'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'yourdb'),
        'USER': os.environ.get('DB_USER', 'yourusername'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'yourpassword'),
        'HOST': os.environ.get('DB_HOST', 'yourhost'),
        'PORT': os.environ.get('DB_PORT', 'yourport'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        # For production, consider using Redis or Memcached:
        # 'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        # 'LOCATION': 'redis://127.0.0.1:6379',
    }
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
REPORTS_DIR = os.path.join(MEDIA_ROOT, 'reports')  # Added

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Login URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = '/'

# Email settings
# Email settings - Gmail SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'yourmail@gmail.com'
EMAIL_HOST_PASSWORD = 'djjx opap pldn uslp'  # Using App Password, not regular password
DEFAULT_FROM_EMAIL = 'Bhavi India Fashion <yourmail@gmail.com>'

# Razorpay settings
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'yourrzpid')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'yourrzpkey')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/bhavi_fashion.log'),
            'formatter': 'verbose',
        },
        'payment_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/payment.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'orders': {
            'handlers': ['console', 'payment_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
# Ensure log directory exists
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)