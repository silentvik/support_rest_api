"""
    SUPPORT_API URL Configuration
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('auth/', include('djoser.urls')),  # if djoser is preferable
    # path('auth/', include('djoser.urls.jwt')),  # if djoser is preferable
    path('api/v1/', include('app_support.urls')),
]
