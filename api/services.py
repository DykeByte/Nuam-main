# api/services.py

from django.db.models import Count
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
def registrar_log(usuario: User, operacion: str, calificacion=None, datos_anteriores=None, datos_nuevos=None, ip=None):
    return LogOperacion.objects.create(
        usuario=usuario,
        calificacion=calificacion,
        operacion=operacion,
        datos_anteriores=datos_anteriores,
        datos_nuevos=datos_nuevos,
        ip_address=ip
    )


# -------------------------
# ESTADÍSTICAS DASHBOARD
# -------------------------
def obtener_estadisticas_dashboard(usuario):
    ahora = timezone.now()
    hace_7_dias = ahora - timedelta(days=7)

    # Calificaciones por usuario
    calificaciones = CalificacionTributaria.objects.filter(usuario=usuario)
    total_calificaciones = calificaciones.count()

    # Conteo de cargas
    cargas = CargaMasiva.objects.filter(iniciado_por=usuario)
    total_cargas = cargas.count()

    # Últimas cargas
    recientes = cargas.order_by('-fecha_inicio')[:5]

    return {
        "total_calificaciones": total_calificaciones,
        "total_cargas": total_cargas,
        "ultimas_cargas": [
            {
                "id": c.id,
                "archivo": c.archivo_nombre,
                "estado": c.estado,
                "fecha": c.fecha_inicio
            }
            for c in recientes
        ]
    }


# -------------------------
# AGRUPACIONES GENERALES
# -------------------------
def calificaciones_por_agrupacion(queryset, field):
    return queryset.values(field).annotate(
        total=Count("id")
    ).order_by("-total")


# -------------------------
# ESTADÍSTICAS DE CARGAS MASIVAS
# -------------------------
def estadisticas_cargas(queryset):
    total = queryset.count()
    return {
        "total_cargas": total,
        "pendientes": queryset.filter(estado="PENDING").count(),
        "procesando": queryset.filter(estado="PROCESSING").count(),
        "completadas": queryset.filter(estado="COMPLETED").count(),
        "fallidas": queryset.filter(estado="FAILED").count(),
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
