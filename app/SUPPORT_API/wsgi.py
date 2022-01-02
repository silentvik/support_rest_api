"""
    WSGI config for SUPPORT_API project.
    The default from django is used.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SUPPORT_API.settings')

application = get_wsgi_application()
