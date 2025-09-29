from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from applications.bodegas.models import Bodega  # 👈 importa tu modelo

# Create your models here.


class Usuario(AbstractUser):
    rol_choices = [
        ('admin', 'Administrador'),
        ('contable', 'Contable'),
        ('almacen', 'Almacen'), 
        ('empleado', 'Empleado'),
    ]
    estado_choices = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    
    # Definir rol y estado con las opciones predefinidas
    rol = models.CharField(max_length=10, choices=rol_choices, default='Almacen')
    estado = models.CharField(max_length=10, choices=estado_choices, default='activo')  # Cambiado a CharField
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # La fecha de último login ya está definida en AbstractUser
    # Si deseas mantenerla, usa 'last_login' que ya está en el modelo base
    
    # 👇 Aquí agregamos la sucursal
    sucursal = models.ForeignKey(
        Bodega,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuarios",
        verbose_name="Sucursal"
    )
    
    def __str__(self):
        return self.username
    
    @property
    def nombre_completo(self):
        return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'