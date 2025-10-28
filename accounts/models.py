# accounts/models.py
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    aprobado = models.BooleanField(default=False)
    rut = models.CharField('RUT', max_length=12, blank=True)
    nombre_completo = models.CharField('Nombre completo', max_length=255, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"


@receiver(post_save, sender=User)
def crear_o_actualizar_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)
    instance.perfil.save()


class CargaMasiva(models.Model):
    TIPO_CHOICES = [
        ('FACTORES', 'Factores'),
        ('MONITOR', 'Monitor'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo_carga = models.CharField(max_length=50, choices=TIPO_CHOICES)
    nombre_archivo = models.CharField(max_length=255)
    registros_procesados = models.IntegerField(default=0)
    registros_exitosos = models.IntegerField(default=0)
    registros_fallidos = models.IntegerField(default=0)
    errores_detalle = models.TextField(blank=True)
    fecha_carga = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_carga']
    
    def __str__(self):
        return f"{self.tipo_carga} - {self.fecha_carga.strftime('%d/%m/%Y')}"


class CalificacionTributaria(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    carga_masiva = models.ForeignKey(CargaMasiva, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Datos principales
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
    
    # NUEVOS CAMPOS PARA CONVERSIÓN
    valor_convertido = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)


    
    # Factores del 8 al 37
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
    
    def __str__(self):
        return f"{self.instrumento} - {self.corredor_dueno}"


class LogOperacion(models.Model):
    OPERACION_CHOICES = [
        ('CREATE', 'Crear'),
        ('UPDATE', 'Actualizar'),
        ('DELETE', 'Eliminar'),
        ('CARGA', 'Carga'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    calificacion = models.ForeignKey(CalificacionTributaria, on_delete=models.SET_NULL, null=True, blank=True)
    carga_masiva = models.ForeignKey(CargaMasiva, on_delete=models.SET_NULL, null=True, blank=True)
    operacion = models.CharField(max_length=50, choices=OPERACION_CHOICES)
    datos_anteriores = models.JSONField(null=True, blank=True)
    datos_nuevos = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"{self.operacion} - {self.usuario.username}"