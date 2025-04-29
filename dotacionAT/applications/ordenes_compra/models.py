from django.db import models
from applications.proveedores.models import Proveedor
from applications.productos.models import Producto
from django.utils.html import format_html
# Create your models here.



class OrdenCompra(models.Model):
    ESTADO_CHOICES = [
        ('generada', 'generada'),
        ('recibida', 'recibida'),
        ('cancelada', 'cancelada'),
    ]

    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    fecha_creacion = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='generada')
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return str(self.id)
    
    @property
    def tipo_documento(self):
        return "OC"


class ItemOrdenCompra(models.Model):
    orden = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.producto.nombre} ({self.cantidad})"
    
    @property
    def tipo_documento(self):
        return "OC"
    
    
class Compra(models.Model):
    orden_compra = models.OneToOneField(OrdenCompra, on_delete=models.CASCADE, related_name='compra')
    fecha_recepcion = models.DateField(auto_now_add=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Compra de orden #{self.orden_compra.id}"
    
    @property
    def tipo_documento(self):
        return "CP"

class ItemCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_recibida = models.PositiveIntegerField(null=True, blank=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def subtotal(self):
        if self.cantidad_recibida is not None and self.precio_unitario is not None:
            return self.cantidad_recibida * self.precio_unitario
        return 0

    def __str__(self):
        return f"{self.producto.nombre} - Recibidos: {self.cantidad_recibida}"    
    
    def subtotal(self):
        if self.cantidad_recibida is not None and self.precio_unitario is not None:
            return self.cantidad_recibida * self.precio_unitario
        return 0

    def subtotal_formateado(self):
        subtotal = self.subtotal()
        return "${:,.2f}".format(subtotal)
    subtotal_formateado.short_description = 'Subtotal'
    
    @property
    def tipo_documento(self):
        return "CP"