from django.db import models
from django.conf import settings  # Importa settings para acceder al modelo de Usuario

class Ciudad(models.Model):
    id_ciudad = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, verbose_name="Nombre de la ciudad")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    activo = models.BooleanField(default=True, verbose_name="Activo/Inactivo")  # Activo/Inactivo
    
    # Agregar el campo de relación con el modelo Usuario
    id_usuario_insert = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Se usa settings.AUTH_USER_MODEL para referirse al modelo de usuario (por si usas un modelo personalizado)
        on_delete=models.SET_NULL,  # El usuario puede ser eliminado, pero no se eliminará la ciudad
        null=True,  # Permitir que este campo sea null
        blank=True,  # Permitir que no se asigne un usuario al crear la ciudad
        related_name='ciudades_insertadas',  # Nombre para acceder a las ciudades relacionadas desde el usuario
        verbose_name="Usuario Creo"
    )
    
    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'
        db_table = 'ciudad'  # Nombre personalizado de la tabla en la base de datos