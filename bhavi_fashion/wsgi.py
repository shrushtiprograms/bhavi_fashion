"""
WSGI config for bhavi_fashion project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bhavi_fashion.settings')

application = get_wsgi_application()
