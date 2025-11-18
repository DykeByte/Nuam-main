from django.contrib import admin
from api.models import (
    Calificacion,
    CargaMasiva,
    CalificacionTributaria,
    LogAuditoria,
    LogOperacion,
    Divisa,
)

admin.site.register(Calificacion)
admin.site.register(CalificacionTributaria)
admin.site.register(CargaMasiva)
admin.site.register(LogAuditoria)
admin.site.register(LogOperacion)
admin.site.register(Divisa)
