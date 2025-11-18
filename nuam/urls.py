# nuam/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuración Swagger/OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="NUAM API",
        default_version='v1',
        description="""
        API REST para el Sistema de Gestión de Calificaciones Tributarias NUAM.

        ## Características:
        - Autenticación con JWT
        - CRUD de calificaciones tributarias
        - Gestión de cargas masivas
        - Logs de auditoría
        - Estadísticas y reportes

        ## Autenticación:
        1. Obtener token: POST /api/v1/auth/token/ con username y password
        2. Usar token en header: Authorization: Bearer {token}
        3. Refrescar token: POST /api/v1/auth/token/refresh/
        """,
        terms_of_service="https://www.nuam.com/terms/",
        contact=openapi.Contact(email="contacto@nuam.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Web tradicional (HTML)
    path('accounts/', include('accounts.urls')),

    # API REST
    path('api/v1/', include('api.urls')),

    # Documentación de la API
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
    path('swagger/',
         schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/',
         schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
    path('api/docs/',
         schema_view.with_ui('swagger', cache_timeout=0),
         name='api-docs'),
]

# Configurar título del admin
admin.site.site_header = "NUAM - Administración"
admin.site.site_title = "NUAM Admin"
admin.site.index_title = "Panel de Administración"


# nuam/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('accounts:home')
    else:
        return redirect('accounts:login')

urlpatterns = [
    path('', root_redirect),  # <- la raíz '/'
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # todas las URLs de accounts
    path('api/v1/', include('api.urls')),        # todas las URLs de la API
]
