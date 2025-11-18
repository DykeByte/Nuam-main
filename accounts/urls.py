# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Autenticación
    path('registro/', views.registro, name='registro'),
    path('login/', views.mi_login, name='login'),
    path('logout/', views.mi_logout, name='logout'),

    # Dashboard/Home
    path('home/', views.home, name='home'),  # <- cambio de '' a 'home/'

    # Cargas Masivas
    path('cargas/', views.lista_cargas, name='lista_cargas'),
    path('cargas/nueva/', views.nueva_carga, name='nueva_carga'),
    path('cargas/<int:pk>/', views.detalle_carga, name='detalle_carga'),
    path('cargas/plantilla/', views.descargar_plantilla, name='descargar_plantilla'),

    # Calificaciones Tributarias
    path('calificaciones/', views.lista_calificaciones, name='lista_calificaciones'),
    path('calificaciones/<int:pk>/', views.detalle_calificacion, name='detalle_calificacion'),
    path('calificaciones/<int:pk>/editar/', views.editar_calificacion, name='editar_calificacion'),
    path('calificaciones/<int:pk>/eliminar/', views.eliminar_calificacion, name='eliminar_calificacion'),

    # Logs/Auditoría
    path('logs/', views.lista_logs, name='lista_logs'),
]
