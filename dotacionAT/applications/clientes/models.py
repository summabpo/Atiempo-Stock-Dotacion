from django.db import models
from django.conf import settings
from applications.ciudades.models import Ciudad # Suponiendo que tienes un modelo de Ciudad en otra aplicación
# Create your models here.

class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)  
    nombre = models.CharField(max_length=255)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, null=True)  # Relación con Ciudad
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    usuario_creador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True) # Relación con User
    activo = models.BooleanField(default=True, verbose_name="Activo/Inactivo")
    
    usuario_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clientes_editados'
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Cliente"