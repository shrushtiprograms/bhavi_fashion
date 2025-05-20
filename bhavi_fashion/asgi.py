"""
ASGI config for bhavi_fashion project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bhavi_fashion.settings')

application = get_asgi_application()
