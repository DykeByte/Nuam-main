# nuam-main/api/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone


# ---------------------
# Modelo: Calificacion (general)
# ---------------------
class Calificacion(models.Model):
    TIPO_CALIFICACION_CHOICES = [
        ('AAA', 'AAA - Máxima Calidad'),
        ('AA', 'AA - Alta Calidad'),
        ('A', 'A - Calidad Media-Alta'),
        ('BBB', 'BBB - Calidad Media'),
        ('BB', 'BB - Especulativo'),
        ('B', 'B - Altamente Especulativo'),
        ('CCC', 'CCC - Riesgo Sustancial'),
        ('CC', 'CC - Muy Alto Riesgo'),
        ('C', 'C - Riesgo Extremo'),
        ('D', 'D - Default'),
    ]

    entidad = models.CharField(max_length=200, db_index=True, help_text="Nombre de la entidad calificada")
    tipo_calificacion = models.CharField(max_length=10, choices=TIPO_CALIFICACION_CHOICES, db_index=True,
                                         help_text="Tipo de calificación crediticia")
    puntaje = models.DecimalField(max_digits=5, decimal_places=2,
                                  validators=[MinValueValidator(0), MaxValueValidator(100)],
                                  help_text="Puntaje numérico de 0 a 100")
    fecha_calificacion = models.DateTimeField(default=timezone.now, db_index=True, help_text="Fecha de la calificación")
    agencia_calificadora = models.CharField(max_length=100, help_text="Agencia que emitió la calificación")
    observaciones = models.TextField(blank=True, null=True, help_text="Observaciones adicionales")

    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='calificaciones_creadas')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True, db_index=True, help_text="Estado de la calificación")

    class Meta:
        db_table = 'api_calificaciones'
        ordering = ['-fecha_calificacion']
        verbose_name = 'Calificación'
        verbose_name_plural = 'Calificaciones'
        indexes = [
            models.Index(fields=['entidad', 'fecha_calificacion']),
            models.Index(fields=['tipo_calificacion', 'activo']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(puntaje__gte=0) & models.Q(puntaje__lte=100),
                                   name='puntaje_rango_valido'),
            models.UniqueConstraint(fields=['entidad', 'agencia_calificadora', 'fecha_calificacion'],
                                    name='calificacion_unica_por_entidad_fecha'),
        ]

    def __str__(self):
        return f"{self.entidad} - {self.tipo_calificacion} ({self.fecha_calificacion.date()})"

    def save(self, *args, **kwargs):
        # Normalizar entidad
        if self.entidad:
            self.entidad = self.entidad.strip().upper()
        super().save(*args, **kwargs)


# ---------------------
# Modelo: CargaMasiva (completo)
# ---------------------
class CargaMasiva(models.Model):
    ESTADO_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('PROCESSING', 'Procesando'),
        ('COMPLETED', 'Completado'),
        ('FAILED', 'Fallido'),
    ]

    archivo_nombre = models.CharField(max_length=255)
    archivo_path = models.CharField(max_length=500, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDING', db_index=True)
    total_registros = models.IntegerField(default=0)
    registros_procesados = models.IntegerField(default=0)
    registros_exitosos = models.IntegerField(default=0)
    registros_fallidos = models.IntegerField(default=0)
    mensaje_error = models.TextField(blank=True, null=True)
    iniciado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cargas_iniciadas')
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'api_cargas_masivas'
        ordering = ['-fecha_inicio']
        verbose_name = 'Carga Masiva'
        verbose_name_plural = 'Cargas Masivas'
        indexes = [
            models.Index(fields=['estado', 'fecha_inicio']),
        ]

    def __str__(self):
        return f"Carga {self.id} - {self.archivo_nombre} ({self.estado})"

    @property
    def duracion(self):
        if self.fecha_fin:
            return (self.fecha_fin - self.fecha_inicio).total_seconds()
        return None

    @property
    def porcentaje_progreso(self):
        if self.total_registros > 0:
            return (self.registros_procesados / self.total_registros) * 100
        return 0


# ---------------------
# Modelo: CalificacionTributaria (detallado con factores 8..37)
# ---------------------
class CalificacionTributaria(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calificaciones_tributarias')
    carga_masiva = models.ForeignKey(CargaMasiva, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='calificaciones_tributarias')

    corredor_dueno = models.CharField(max_length=255, blank=True)
    rut_es_el_manual = models.CharField(max_length=12, blank=True)
    ano_comercial = models.CharField(max_length=50, blank=True)
    mercado = models.CharField(max_length=50, blank=True)
    instrumento = models.CharField(max_length=100, blank=True)
    fecha_pago = models.DateField(null=True, blank=True)
    secuencia_evento = models.IntegerField(null=True, blank=True)
    numero_dividendo = models.IntegerField(null=True, blank=True)
    descripcion = models.CharField(max_length=255, blank=True)
    tipo_sociedad = models.CharField(max_length=10, blank=True)
    divisa = models.CharField(max_length=10, default='CLP')
    acopio_lsfxf = models.BooleanField(default=False)
    valor_historico = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    factor_actualizacion = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    valor_convertido = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    # Factores 8..37
    factor_8 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_9 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_10 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_11 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_12 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_13 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_14 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_15 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_16 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_17 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_18 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_19 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_20 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_21 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_22 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_23 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_24 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_25 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_26 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_27 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_28 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_29 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_30 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_31 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_32 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_33 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_34 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_35 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_36 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    factor_37 = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)

    origen = models.CharField(max_length=255, blank=True)
    es_local = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Calificación Tributaria'
        verbose_name_plural = 'Calificaciones Tributarias'

    def __str__(self):
        return f"{self.instrumento} - {self.corredor_dueno}"


# ---------------------
# Modelo: LogAuditoria (más genérico)
# ---------------------
class LogAuditoria(models.Model):
    ACCION_CHOICES = [
        ('CREATE', 'Crear'),
        ('UPDATE', 'Actualizar'),
        ('DELETE', 'Eliminar'),
        ('READ', 'Leer'),
        ('LOGIN', 'Inicio de Sesión'),
        ('LOGOUT', 'Cierre de Sesión'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='logs_auditoria')
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES, db_index=True)
    modelo = models.CharField(max_length=100, help_text="Modelo afectado")
    objeto_id = models.IntegerField(null=True, blank=True, help_text="ID del objeto afectado")
    datos_anteriores = models.JSONField(null=True, blank=True, help_text="Datos antes del cambio")
    datos_nuevos = models.JSONField(null=True, blank=True, help_text="Datos después del cambio")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'api_logs_auditoria'
        ordering = ['-timestamp']
        verbose_name = 'Log de Auditoría'
        verbose_name_plural = 'Logs de Auditoría'
        indexes = [
            models.Index(fields=['usuario', 'timestamp']),
            models.Index(fields=['accion', 'modelo']),
        ]

    def __str__(self):
        return f"{self.usuario} - {self.accion} en {self.modelo} ({self.timestamp})"


# ---------------------
# Modelo: LogOperacion (operaciones vinculadas a CalificacionTributaria / CargaMasiva)
# ---------------------
class LogOperacion(models.Model):
    OPERACION_CHOICES = [
        ('CREATE', 'Crear'),
        ('UPDATE', 'Actualizar'),
        ('DELETE', 'Eliminar'),
        ('CARGA', 'Carga'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    calificacion = models.ForeignKey(CalificacionTributaria, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='logs_operacion')
    carga_masiva = models.ForeignKey(CargaMasiva, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='logs_operacion')
    operacion = models.CharField(max_length=50, choices=OPERACION_CHOICES)
    datos_anteriores = models.JSONField(null=True, blank=True)
    datos_nuevos = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_hora']
        verbose_name = 'Log de Operación'
        verbose_name_plural = 'Logs de Operación'

    def __str__(self):
        return f"{self.operacion} - {self.usuario.username}"


# ---------------------
# Modelo: Divisa
# ---------------------
class Divisa(models.Model):
    codigo = models.CharField(max_length=3, unique=True, db_index=True, help_text="Código ISO (USD, EUR, CLP)")
    nombre = models.CharField(max_length=100)
    simbolo = models.CharField(max_length=10, blank=True)
    tasa_cambio_usd = models.DecimalField(max_digits=15, decimal_places=6, help_text="Tasa respecto a USD")
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'api_divisas'
        ordering = ['codigo']
        verbose_name = 'Divisa'
        verbose_name_plural = 'Divisas'

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
