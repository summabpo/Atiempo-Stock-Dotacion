from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Sum

from .models import InventarioBodega
from applications.ordenes_compra.models import ItemCompra
from applications.ordenes_salida.models import ItemSalida
from applications.productos.models import Producto

# 🟢 Entrada por compra
@receiver(post_save, sender=ItemCompra)
def actualizar_inventario_y_producto(sender, instance, created, **kwargs):
    if created and instance.compra.bodega:
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

        # Actualizar el costo del producto
        producto = instance.producto
        producto.costo = instance.precio_unitario
        producto.save(update_fields=['costo'])

        # Actualizar stock total del producto en todas las bodegas
        stock_total = InventarioBodega.objects.filter(producto=producto).aggregate(
            total=Sum('stock')
        )['total'] or 0

        producto.stock = stock_total
        producto.save(update_fields=['stock'])

# 🔴 Salida de productos y traslado entre bodegas
@receiver(post_save, sender=ItemSalida)
def actualizar_inventario_salida(sender, instance, created, **kwargs):
    if not created:
        return

    producto = instance.producto
    cantidad = instance.cantidad or 0
    salida = instance.salida

    if cantidad <= 0 or not producto:
        return

    # 1. Salida de la bodega origen
    if salida.bodegaSalida:
        inventario_salida, _ = InventarioBodega.objects.get_or_create(
            bodega=salida.bodegaSalida,
            producto=producto
        )
        inventario_salida.salidas += cantidad
        inventario_salida.stock -= cantidad
        inventario_salida.ultima_salida = timezone.now()
        inventario_salida.save()
        print(f"📤 Producto '{producto.nombre}' salido de {salida.bodegaSalida.nombre}: -{cantidad}")

    # 2. Entrada a la bodega destino (si aplica)
    if salida.bodegaEntrada:
        inventario_entrada, _ = InventarioBodega.objects.get_or_create(
            bodega=salida.bodegaEntrada,
            producto=producto
        )
        inventario_entrada.entradas += cantidad
        inventario_entrada.stock += cantidad
        inventario_entrada.ultima_entrada = timezone.now()
        inventario_entrada.save()
        print(f"📥 Producto '{producto.nombre}' recibido en {salida.bodegaEntrada.nombre}: +{cantidad}")

    # 3. Actualizar stock total del producto en todas las bodegas
    stock_total = InventarioBodega.objects.filter(producto=producto).aggregate(
        total=Sum('stock')
    )['total'] or 0

    producto.stock = stock_total
    producto.save(update_fields=['stock'])