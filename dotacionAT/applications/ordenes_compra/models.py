from django.db import models
from applications.proveedores.models import Proveedor
from applications.productos.models import Producto
from applications.bodegas.models import Bodega
from django.utils.html import format_html
from decimal import Decimal
from django.conf import settings
# Create your models here.



class OrdenCompra(models.Model):
    ESTADO_CHOICES = [
        ('generada', 'generada'),
        ('recibida', 'recibida'),
        ('comprada', 'comprada'),
        ('cancelada', 'cancelada'),
    ]

    TIPO_CHOICES = [
        ('OC', 'Orden de Compra'),
        ('TR', 'Traslado Interno'),
    ]

    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='generada')
    observaciones = models.TextField(blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    usuario_creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordenes_creadas'
    )

    tipo_documento = models.CharField(
        max_length=2,
        choices=TIPO_CHOICES,
        default="OC"
    )

    def __str__(self):
        return f"{self.id} - {self.get_tipo_documento_display()}"


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
    
    
# class Compra(models.Model):
#     orden_compra = models.OneToOneField(OrdenCompra, on_delete=models.CASCADE, related_name='compra')
#     fecha_recepcion = models.DateField(auto_now_add=True)
#     observaciones = models.TextField(blank=True)
     
#     total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

#     def __str__(self):
#         return f"Compra de orden #{self.orden_compra.id}"
    
#     @property
#     def tipo_documento(self):
#         return "OR"

class Compra(models.Model):
    # orden_compra = models.OneToOneField(OrdenCompra, on_delete=models.CASCADE, related_name='compra')
    orden_compra = models.OneToOneField(
        OrdenCompra,
        on_delete=models.CASCADE,
        related_name='compra',
        null=True,       # 👈 importante
        blank=True       # 👈 importante
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    estado = models.CharField(max_length=20, default='Compra')
    # ✅ NUEVOS CAMPOS
    bodega = models.ForeignKey(Bodega, on_delete=models.SET_NULL, null=True, blank=True, related_name='compras')
    numero_factura = models.CharField(max_length=50, blank=True, verbose_name="Número de Factura")
    proveedor = models.ForeignKey(Proveedor, null=True, on_delete=models.CASCADE)
       
    usuario_creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True, related_name="compras_creadas")
    

    def __str__(self):
        if self.orden_compra:
            return f"Compra de orden #{self.orden_compra.id}"
        return f"Compra sin orden asociada #{self.id}"

    @property
    def tipo_documento(self):
        if self.orden_compra:
            return "CP"  # Orden Regular
        return "TR" 


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
        return "OR"