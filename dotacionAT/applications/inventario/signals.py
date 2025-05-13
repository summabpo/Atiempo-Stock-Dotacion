from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Sum

from .models import InventarioBodega
from applications.ordenes_compra.models import ItemCompra
from applications.productos.models import Producto

# @receiver(post_save, sender=ItemCompra)
# def actualizar_inventario(sender, instance, created, **kwargs):
#     if not created:
#         return

#     bodega = instance.compra.bodega
#     producto = instance.producto
#     cantidad = instance.cantidad_recibida or 0

#     if not bodega or cantidad <= 0:
#         return

#     inventario, creado_nuevo = InventarioBodega.objects.get_or_create(
#         bodega=bodega,
#         producto=producto
#     )
#     inventario.entradas += cantidad
#     inventario.stock += cantidad
#     inventario.ultima_entrada = timezone.now()
#     inventario.save()

@receiver(post_save, sender=ItemCompra)
def actualizar_inventario_y_producto(sender, instance, created, **kwargs):
    if created and instance.compra.bodega:
        # Paso 1: Actualizar inventario de la bodega específica
        inventario, _ = InventarioBodega.objects.get_or_create(
            bodega=instance.compra.bodega,
            producto=instance.producto
        )
        cantidad = instance.cantidad_recibida or 0
        inventario.entradas += cantidad
        inventario.stock += cantidad
        inventario.ultima_entrada = timezone.now()
        inventario.save()

        print(f"✅ Inventario actualizado para: {instance.producto.nombre} en {instance.compra.bodega.nombre}")

        # Paso 2: Actualizar el costo del producto
        producto = instance.producto
        producto.costo = instance.precio_unitario  # O haz un promedio ponderado si deseas
        producto.save(update_fields=['costo'])

        # Paso 3: Actualizar stock total del producto (sumando en todas las bodegas)
        stock_total = InventarioBodega.objects.filter(producto=producto).aggregate( 
            total=Sum('stock')
        )['total'] or 0

        producto.stock = stock_total
        producto.save(update_fields=['stock'])

        # print(f"🔁 Producto actualizado: {producto.nombre} | Nuevo costo: {producto.costo} | Stock total: {producto.stock}")