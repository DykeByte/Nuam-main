# api/services.py

from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from api.models import LogOperacion, CargaMasiva, CalificacionTributaria
from .excel_handler import ExcelHandler
from forex_python.converter import CurrencyRates
import pandas as pd
from io import BytesIO


# -------------------------
# LOGGING DE OPERACIONES
# -------------------------
def registrar_log(usuario, operacion, objeto, datos_anteriores=None, datos_nuevos=None):
    """Registra una operación en el log"""
    from api.models import LogOperacion
    
    log_data = {
        'usuario': usuario,
        'operacion': operacion,
        'datos_anteriores': datos_anteriores,
        'datos_nuevos': datos_nuevos,
    }
    
    if objeto and hasattr(objeto, '__class__'):
        if objeto.__class__.__name__ == 'CalificacionTributaria':
            log_data['calificacion'] = objeto
        elif objeto.__class__.__name__ == 'CargaMasiva':
            log_data['carga_masiva'] = objeto
    
    return LogOperacion.objects.create(**log_data)



# -------------------------
# ESTADÍSTICAS DASHBOARD
# -------------------------
def obtener_estadisticas_dashboard(usuario):
    """
    Obtiene estadísticas generales del dashboard para un usuario.
    """
    calificaciones = CalificacionTributaria.objects.filter(usuario=usuario)
    cargas = CargaMasiva.objects.filter(iniciado_por=usuario)
    
    # Agrupar por mercado
    por_mercado = {}
    for item in calificaciones.values('mercado').annotate(total=Count('id')):
        por_mercado[item['mercado']] = item['total']
    
    # Agrupar por divisa
    por_divisa = {}
    for item in calificaciones.values('divisa').annotate(total=Count('id')):
        por_divisa[item['divisa']] = item['total']
    
    # Agrupar por tipo de carga
    por_tipo_carga = {}
    for item in cargas.values('tipo_carga').annotate(total=Count('id')):
        por_tipo_carga[item['tipo_carga']] = item['total']
    
    # Calcular tasa de éxito
    total_procesados = cargas.aggregate(Sum('registros_procesados'))['registros_procesados__sum'] or 0
    total_exitosos = cargas.aggregate(Sum('registros_exitosos'))['registros_exitosos__sum'] or 0
    tasa_exito = round((total_exitosos / total_procesados * 100), 2) if total_procesados > 0 else 0
    
    return {
        'total_calificaciones': calificaciones.count(),
        'total_cargas': cargas.count(),
        'cargas_exitosas': cargas.filter(estado='COMPLETADO').count(),  # ← CORREGIDO
        'cargas_con_errores': cargas.filter(estado='COMPLETADO_CON_ERRORES').count(),  # ← CORREGIDO
        'tasa_exito': tasa_exito,
        'por_mercado': por_mercado,
        'por_divisa': por_divisa,
        'por_tipo_carga': por_tipo_carga,
        'ultimas_cargas': cargas.order_by('-fecha_inicio')[:5],
    }




# -------------------------
# AGRUPACIONES GENERALES
# -------------------------
def calificaciones_por_agrupacion(queryset, campo):
    """
    Agrupa calificaciones por un campo específico.
    """
    return queryset.values(campo).annotate(
        total=Count('id'),
        valor_total=Sum('valor_historico')
    ).order_by('-total')

# -------------------------
# ESTADÍSTICAS DE CARGAS MASIVAS
# -------------------------
def estadisticas_cargas(queryset):
    """
    Calcula estadísticas de cargas masivas.
    """
    return {
        'total': queryset.count(),
        'completadas': queryset.filter(estado='COMPLETADO').count(),
        'con_errores': queryset.filter(estado='COMPLETADO_CON_ERRORES').count(),
        'procesando': queryset.filter(estado='PROCESANDO').count(),
        'total_registros': queryset.aggregate(Sum('registros_procesados'))['registros_procesados__sum'] or 0,
        'total_exitosos': queryset.aggregate(Sum('registros_exitosos'))['registros_exitosos__sum'] or 0,
        'total_fallidos': queryset.aggregate(Sum('registros_fallidos'))['registros_fallidos__sum'] or 0,
    }



# -------------------------
# PROCESAR CARGA MASIVA DE EXCEL
# -------------------------
def procesar_carga_masiva(tipo_carga, archivo, usuario, mercado):
    handler = ExcelHandler(archivo, tipo_carga, usuario, mercado)
    carga = handler.procesar()

    # Conversion monetaria
    c = CurrencyRates()
    for calificacion in carga.calificaciontributaria_set.all():
        if calificacion.divisa and calificacion.valor_historico:
            try:
                valor = c.convert(calificacion.divisa, "CLP", calificacion.valor_historico)
                calificacion.valor_convertido = round(valor, 2)
                calificacion.save()
            except Exception:
                pass

    return carga



# -------------------------
# GENERAR PLANTILLA EXCEL
# -------------------------
def generar_plantilla_excel():
    df = pd.DataFrame(columns=[
        "corredor_dueno", "descripcion", "valor_historico", "divisa", "ano_comercial", "es_local",
        "mercado", "instrumento", "numero_dividendo", "fecha_pago", "origen"
    ])

    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return output.getvalue()
