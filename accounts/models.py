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
    else:
        instance.perfil.save()
