"""
URLs para el módulo de Kafka
Incluir en nuam/urls.py con: path('kafka/', include('kafka_app.urls'))
"""
from django.urls import path
from kafka_app import views

app_name = 'kafka'

urlpatterns = [
    # Dashboard de monitoreo
    path('dashboard/', views.kafka_dashboard_view, name='dashboard'),
    
    # ← AGREGAR ESTOS
    path('metrics/', views.metrics_view, name='metrics'),
    path('metrics/dashboard/', views.metrics_dashboard, name='metrics_dashboard'),
    
    # Health check
    path('health/', views.kafka_health_check, name='health_check'),
]