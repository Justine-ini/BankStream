from django.conf import settings
# from .settings.local import ADMIN_URL
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
]
