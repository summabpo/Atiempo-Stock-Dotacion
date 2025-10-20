from django.db import models
from applications.clientes.models import Cliente
from applications.productos.models import Producto
from applications.bodegas.models import Bodega
from applications.ordenes_compra.models import OrdenCompra
from django.utils.html import format_html
from decimal import Decimal
from django.conf import settings

# Create your models here.
class Salida(models.Model):

    tipo_documento = models.CharField(
        max_length=2,
        verbose_name="Tipo de Documento"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    estado = models.CharField(max_length=20, default='Salida')
    bodegaSalida = models.ForeignKey(Bodega, on_delete=models.SET_NULL, null=True, blank=True, related_name='salida')
    bodegaEntrada = models.ForeignKey(Bodega, on_delete=models.SET_NULL, null=True, blank=True, related_name='entrada')
    cliente = models.ForeignKey(Cliente, null=True, on_delete=models.CASCADE)
    
    usuario_creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True, related_name="salidas_creadas")
    
    # 👇 Nueva relación
    orden_compra_asociada = models.ForeignKey(
        OrdenCompra,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='salidas_relacionadas'
    )

    def __str__(self):
        return f"Salida {self.id} - {self.tipo_documento}"
    
class ItemSalida(models.Model):
    salida = models.ForeignKey(Salida, on_delete=models.CASCADE, related_name='items_salida')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(null=True, blank=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def subtotal(self):
        if self.cantidad is not None and self.precio_unitario is not None:
            return self.cantidad * self.precio_unitario
        return 0

    def subtotal_formateado(self):
        subtotal = self.subtotal()
        return "${:,.2f}".format(subtotal)
    subtotal_formateado.short_description = 'Subtotal'

    @property
    def tipo_documento(self):
        return self.salida.tipo_documento  # Hereda el tipo del documento padre

    def __str__(self):
        return f"{self.producto.nombre} - Recibidos: {self.cantidad}"