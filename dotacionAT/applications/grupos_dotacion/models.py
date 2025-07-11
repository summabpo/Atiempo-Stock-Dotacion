from django.db import models
from applications.ciudades.models import Ciudad
from applications.clientes.models import Cliente # Asumiendo que ya tienes esta app
from applications.productos.models import Producto
from django.conf import settings  # O tu modelo de usuario

# Create your models here.

class Cargo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True, verbose_name="Activo/Inactivo")

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

class GrupoDotacion(models.Model):
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE)
    genero = models.CharField(max_length=10, choices=[('MASCULINO', 'Masculino'), ('FEMENINO', 'Femenino')])
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cargo} - {self.cliente} - {self.ciudad} - {self.genero}"

class GrupoDotacionProducto(models.Model):
    grupo = models.ForeignKey(GrupoDotacion, on_delete=models.CASCADE, related_name='productos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        estado = "Activo" if self.producto.activo else "Inactivo"
        return f"{self.estado} - {estado} x {self.cantidad} en {self.grupo}"