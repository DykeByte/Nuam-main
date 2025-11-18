# api/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from api.views import (
    CalificacionTributariaViewSet,
    CargaMasivaViewSet,
    LogOperacionViewSet,
    registro_api,
    dashboard_stats,
    health_check,
    PerfilViewSet
)

# Crear router DRF
router = DefaultRouter()
router.register(r'perfiles', PerfilViewSet, basename='perfil')
router.register(r'calificaciones', CalificacionTributariaViewSet, basename='calificacion')
router.register(r'cargas', CargaMasivaViewSet, basename='carga')
router.register(r'logs', LogOperacionViewSet, basename='log')

app_name = 'api'

urlpatterns = [
    # Health check
    path('health/', health_check, name='health'),
    
    # Autenticación JWT
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/register/', registro_api, name='register'),
    
    # Dashboard stats API
    path('dashboard/stats/', dashboard_stats, name='dashboard_stats'),
    
    # Endpoints CRUD con router
    path('', include(router.urls)),
]
