from django.db import models

from applications.grupos_dotacion.models import GrupoDotacion  # ajusta el import si es necesario
from applications.productos.models import Producto
from applications.clientes.models import Cliente

# Create your models here.

class EmpleadoDotacion(models.Model):
    cedula = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)
    #ciudad = models.ForeignKey(Ciudad, on_delete=models.PROTECT, default=1)
    ciudad = models.CharField(max_length=50, null=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    cargo = models.CharField(max_length=100)
    #cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    cliente = models.CharField(max_length=255)
    centro_costo = models.CharField(max_length=100)
    sexo = models.CharField(max_length=20)

    talla_camisa = models.CharField(max_length=20, blank=True, null=True)
    cantidad_camisa = models.PositiveIntegerField(default=0, blank=True, null=True)

    talla_pantalon = models.CharField(max_length=20, blank=True, null=True)
    cantidad_pantalon = models.PositiveIntegerField(default=0, blank=True, null=True)

    talla_zapatos = models.CharField(max_length=20, blank=True, null=True)
    
    cantidad_zapatos = models.PositiveIntegerField(default=0, blank=True, null=True)

    cantidad_botas_caucho = models.PositiveIntegerField(default=0, blank=True, null=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nombre} ({self.cedula})'
    
    
    class Meta:
        verbose_name = "Empleado con Dotación"
        verbose_name_plural = "Empleados con Dotación"
        
    class Meta:
        ordering = ['-fecha_registro']
    
    
class EntregaDotacion(models.Model):
    empleado = models.ForeignKey(EmpleadoDotacion, on_delete=models.CASCADE, related_name='entregas')
    grupo = models.ForeignKey(GrupoDotacion, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Entrega {self.id} - {self.empleado.nombre if self.empleado else 'Sin empleado'}"

    def total_prendas(self):
        return sum(detalle.cantidad for detalle in self.detalles.all())       
    
    
class DetalleEntregaDotacion(models.Model):
    entrega = models.ForeignKey(EntregaDotacion, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"
    
    
    
    
    
