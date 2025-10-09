# accounts/admin.py
from django.contrib import admin
from .models import Perfil, CargaMasiva, CalificacionTributaria, LogOperacion


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'nombre_completo', 'rut', 'aprobado')
    list_editable = ('aprobado',)
    search_fields = ('user__username', 'nombre_completo', 'rut')
    list_filter = ('aprobado',)


@admin.register(CargaMasiva)
class CargaMasivaAdmin(admin.ModelAdmin):
    list_display = ('tipo_carga', 'usuario', 'nombre_archivo', 'registros_procesados', 'registros_exitosos', 'registros_fallidos', 'fecha_carga')
    list_filter = ('tipo_carga', 'fecha_carga')
    search_fields = ('usuario__username', 'nombre_archivo')
    readonly_fields = ('fecha_carga',)
    
    def has_add_permission(self, request):
        # No permitir crear cargas manualmente desde el admin
        return False


@admin.register(CalificacionTributaria)
class CalificacionTributariaAdmin(admin.ModelAdmin):
    list_display = ('instrumento', 'corredor_dueno', 'mercado', 'fecha_pago', 'usuario', 'created_at')
    list_filter = ('mercado', 'tipo_sociedad', 'es_local', 'created_at')
    search_fields = ('instrumento', 'corredor_dueno', 'rut_es_el_manual')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información básica', {
            'fields': ('usuario', 'carga_masiva', 'corredor_dueno', 'rut_es_el_manual')
        }),
        ('Detalles comerciales', {
            'fields': ('ano_comercial', 'mercado', 'instrumento', 'fecha_pago', 'secuencia_evento', 'numero_dividendo')
        }),
        ('Clasificación', {
            'fields': ('descripcion', 'tipo_sociedad', 'acopio_lsfxf', 'valor_historico', 'factor_actualizacion')
        }),
        ('Factores (8-20)', {
            'fields': ('factor_8', 'factor_9', 'factor_10', 'factor_11', 'factor_12', 'factor_13', 'factor_14', 'factor_15', 'factor_16', 'factor_17', 'factor_18', 'factor_19', 'factor_20'),
            'classes': ('collapse',)
        }),
        ('Factores (21-30)', {
            'fields': ('factor_21', 'factor_22', 'factor_23', 'factor_24', 'factor_25', 'factor_26', 'factor_27', 'factor_28', 'factor_29', 'factor_30'),
            'classes': ('collapse',)
        }),
        ('Factores (31-37)', {
            'fields': ('factor_31', 'factor_32', 'factor_33', 'factor_34', 'factor_35', 'factor_36', 'factor_37'),
            'classes': ('collapse',)
        }),
        ('Otros', {
            'fields': ('origen', 'es_local', 'created_at', 'updated_at')
        }),
    )


@admin.register(LogOperacion)
class LogOperacionAdmin(admin.ModelAdmin):
    list_display = ('operacion', 'usuario', 'fecha_hora', 'ip_address')
    list_filter = ('operacion', 'fecha_hora')
    search_fields = ('usuario__username',)
    readonly_fields = ('usuario', 'calificacion', 'carga_masiva', 'operacion', 'datos_anteriores', 'datos_nuevos', 'ip_address', 'fecha_hora')
    date_hierarchy = 'fecha_hora'
    
    def has_add_permission(self, request):
        # Los logs no se crean manualmente
        return False
    
    def has_change_permission(self, request, obj=None):
        # Los logs no se editan
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Solo admin puede eliminar logs
        return request.user.is_superuser