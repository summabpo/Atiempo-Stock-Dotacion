from django.db import models
from applications.ciudades.models import Ciudad
from applications.clientes.models import Cliente # Asumiendo que ya tienes esta app
from applications.productos.models import Producto, Categoria
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
    cargos = models.ManyToManyField(Cargo)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    ciudades = models.ManyToManyField(Ciudad)
    genero = models.CharField(max_length=10, choices=[('MASCULINO', 'Masculino'), ('FEMENINO', 'Femenino')])
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        cargos = ', '.join([str(c) for c in self.cargos.all()])
        ciudades = ', '.join([str(c) for c in self.ciudades.all()])
        return f"{cargos} - {self.cliente} - {ciudades} - {self.genero}"

class GrupoDotacionProducto(models.Model):
    grupo = models.ForeignKey(GrupoDotacion, on_delete=models.CASCADE, related_name='categorias')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, null=True, blank=True)  # <- ¡Así está bien!
    cantidad = models.PositiveIntegerField(default=1)
    activo = models.BooleanField(default=True)

    def __str__(self):
        estado = "Activo" if self.activo else "Inactivo"
        return f"{self.categoria.nombre} - {estado} x{self.cantidad} en {self.grupo}"