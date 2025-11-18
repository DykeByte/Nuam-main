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
    
    

    # API para obtener lag de consumidores
     #path('consumer-lag/', views.kafka_consumer_lag_view, name='consumer_lag'),
]