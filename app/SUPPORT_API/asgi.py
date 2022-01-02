"""
    ASGI config for SUPPORT_API project.
    The default from django is used.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SUPPORT_API.settings')

application = get_asgi_application()
