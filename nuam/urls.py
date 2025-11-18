from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import redirect
from django.conf import settings

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Redirección raíz
def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('accounts:home')
    return redirect('accounts:login')

# Configuración Swagger/OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="NUAM API",
        default_version='v1',
        description="""
        API REST para el Sistema de Gestión de Calificaciones Tributarias NUAM.
        """,
        contact=openapi.Contact(email="contacto@nuam.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Root
    path('', root_redirect),

    # Admin
    path('admin/', admin.site.urls),

    # Autenticación y vistas HTML
    path('accounts/', include('accounts.urls')),

    # API principal
    path('api/v1/', include('api.urls')),

    # Kafka module
    path('kafka/', include('kafka_app.urls')),

    # Swagger / OpenAPI
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),

    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),

    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),

    path(
        'api/docs/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='api-docs'
    ),
]

# Configuración del admin
admin.site.site_header = "NUAM - Administración"
admin.site.site_title = "NUAM Admin"
admin.site.index_title = "Panel de Administración"
