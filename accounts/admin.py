# accounts/admin.py
from django.contrib import admin
from .models import Perfil

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'nombre_completo', 'rut', 'aprobado')
    list_editable = ('aprobado',)
    search_fields = ('user__username', 'nombre_completo', 'rut')
    list_filter = ('aprobado',)

