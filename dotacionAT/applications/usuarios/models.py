from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class Usuario(AbstractUser):
    rol_choices = [
        ('admin', 'Administrador'),
        ('empleado', 'Empleado'),
        ('gerente', 'Gerente'),
    ]
    estado_choices = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    
    # Definir rol y estado con las opciones predefinidas
    rol = models.CharField(max_length=10, choices=rol_choices, default='empleado')
    estado = models.CharField(max_length=10, choices=estado_choices, default='activo')  # Cambiado a CharField
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # La fecha de último login ya está definida en AbstractUser
    # Si deseas mantenerla, usa 'last_login' que ya está en el modelo base
    
    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'