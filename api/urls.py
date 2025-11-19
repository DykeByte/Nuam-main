# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from api.views import (
    CalificacionTributariaViewSet,
    CargaMasivaViewSet,
    LogOperacionViewSet,
    LogAuditoriaViewSet,
    CalificacionViewSet,
    DivisaViewSet,
    PerfilViewSet,
    dashboard_stats,
    registro_api,
    mi_perfil,
    health_check,
    obtener_tasa_cambio,
    convertir_monto,
    obtener_todas_tasas,
    obtener_tasa_ajax,
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'calificaciones', CalificacionTributariaViewSet, basename='calificacion-tributaria')
router.register(r'cargas', CargaMasivaViewSet, basename='carga-masiva')
router.register(r'logs-operacion', LogOperacionViewSet, basename='log-operacion')
router.register(r'logs-auditoria', LogAuditoriaViewSet, basename='log-auditoria')
router.register(r'calificaciones-generales', CalificacionViewSet, basename='calificacion')
router.register(r'divisas', DivisaViewSet, basename='divisa')
router.register(r'perfiles', PerfilViewSet, basename='perfil')

# Schema para Swagger/OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="NUAM API",
        default_version='v1',
        description="""
        API REST para el sistema de gestión de calificaciones tributarias NUAM.
        
        ## Autenticación
        Esta API usa JWT (JSON Web Tokens). Para autenticarte:
        1. Obtén un token en `/api/v1/auth/token/`
        2. Incluye el token en el header: `Authorization: Bearer {tu_token}`
        
        ## Endpoints principales
        - `/api/v1/calificaciones/` - Gestión de calificaciones tributarias
        - `/api/v1/cargas/` - Gestión de cargas masivas
        - `/api/v1/cargas/upload/` - Subir archivos Excel
        - `/api/v1/dashboard/stats/` - Estadísticas del dashboard
        """,
        terms_of_service="https://www.nuam.com/terms/",
        contact=openapi.Contact(email="soporte@nuam.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

app_name = 'api'

urlpatterns = [
    # Autenticación JWT (PRIMERO)
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/registro/', registro_api, name='registro'),
    path('auth/me/', mi_perfil, name='mi-perfil'),
    
    # Conversión de Divisas (ANTES DEL ROUTER)
    path('divisas/tasa/', obtener_tasa_cambio, name='obtener-tasa-cambio'),
    path('divisas/convertir/', convertir_monto, name='convertir-monto'),
    path('divisas/tasas/', obtener_todas_tasas, name='obtener-todas-tasas'),
    path('divisas/tasa-ajax/', obtener_tasa_ajax, name='obtener-tasa-ajax'), 
    
    # Dashboard
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),
    
    # Health Check
    path('health/', health_check, name='health-check'),
    
    # Documentación Swagger/OpenAPI
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # Router URLs (AL FINAL - captura todo lo demás)
    path('', include(router.urls)),
]