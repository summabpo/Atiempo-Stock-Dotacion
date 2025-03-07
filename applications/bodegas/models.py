from django.db import models
from django.conf import settings  # Importamos settings en lugar de Usuario directamente
from applications.ciudades.models import Ciudad  # Relación con Ciudad (suponiendo que la app ciudades ya está creada)

# Create your models here.

class Bodega(models.Model):
    id_bodega = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    id_ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, related_name='bodegas')
    direccion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_edicion = models.DateTimeField(auto_now=True)
    estado = models.CharField(
        max_length=10,
        choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')],
        default='activo'
    )
    id_usuario_creador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bodegas_creadas', null=True, blank=True)
    id_usuario_editor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bodegas_editadas', null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Bodega'
        verbose_name_plural = 'Bodegas'
        db_table = 'bodega'