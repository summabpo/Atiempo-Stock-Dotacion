from django.db import models
from django.conf import settings  # Importa settings para acceder al modelo de Usuario

class Ciudad(models.Model):
    id_ciudad = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, verbose_name="Nombre de la ciudad")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    activo = models.BooleanField(default=True, verbose_name="Activo/Inactivo")

    id_usuario_insert = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ciudades_insertadas',
        verbose_name="Usuario Creo"
    )

    id_usuario_update = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ciudades_actualizadas',
        verbose_name="Usuario Modificó"
    )

    def __str__(self):
        return self.nombre
    class Meta:
        ordering = ['nombre']
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'
        db_table = 'ciudad'