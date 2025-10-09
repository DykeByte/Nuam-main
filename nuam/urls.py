
# ============================================
# nuam/urls.py
# ============================================
"""
URL configuration for nuam project.
"""
from django.contrib import admin
from django.urls import path, include
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', views.home, name='home'),
]