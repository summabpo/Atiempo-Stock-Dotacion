from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
from .models import InventarioBodega
from applications.ordenes_compra.models import ItemCompra, Compra, Proveedor
from applications.ordenes_salida.models import ItemSalida
from applications.productos.models import Producto
from dotacionAT.middleware import get_current_user
#from crum import get_current_user

# ✅ Entrada por compra
@receiver(post_save, sender=ItemCompra)
def actualizar_inventario_y_producto(sender, instance, created, **kwargs):
    usuario = get_current_user()

    if created and instance.compra.bodega:
        inventario, _ = InventarioBodega.objects.get_or_create(
            bodega=instance.compra.bodega,
            producto=instance.producto
        )

        cantidad = instance.cantidad_recibida or 0
        inventario.entradas += cantidad
        inventario.stock += cantidad
        inventario.ultima_entrada = timezone.now()
        inventario.usuario_ultima_entrada = usuario
        inventario.save()

        producto = instance.producto
        producto.costo = instance.precio_unitario
        producto.save(update_fields=['costo'])

        stock_total = InventarioBodega.objects.filter(producto=producto).aggregate(
            total=Sum('stock')
        )['total'] or 0

        producto.stock = stock_total
        producto.save(update_fields=['stock'])

# 🔁 Salida y traslado entre bodegas
@receiver(post_save, sender=ItemSalida)
def actualizar_inventario_salida(sender, instance, created, **kwargs):
    if not created:
        return

    producto = instance.producto
    cantidad = instance.cantidad or 0
    salida = instance.salida

    if cantidad <= 0 or not producto:
        return

    # 🔐 Obtener usuario desde la salida o el middleware
    usuario = salida.usuario_creador or get_current_user()

    # 🟢 Salida desde bodega origen
    if salida.bodegaSalida:
        inventario_salida, _ = InventarioBodega.objects.get_or_create(
            bodega=salida.bodegaSalida,
            producto=producto
        )
        inventario_salida.salidas += cantidad
        inventario_salida.stock -= cantidad
        inventario_salida.ultima_salida = timezone.now()
        inventario_salida.usuario_ultima_salida = usuario
        inventario_salida.save()

    # 🔵 Entrada a bodega destino
    # if salida.bodegaEntrada:
    #     inventario_entrada, _ = InventarioBodega.objects.get_or_create(
    #         bodega=salida.bodegaEntrada,
    #         producto=producto
    #     )
    #     inventario_entrada.entradas += cantidad
    #     inventario_entrada.stock += cantidad
    #     inventario_entrada.ultima_entrada = timezone.now()
    #     inventario_entrada.usuario_ultima_entrada = usuario
    #     inventario_entrada.save()

    #     # 🧾 Si es un TRASLADO, crear Compra automáticamente
    #     if salida.tipo_documento == 'TR':
    #         proveedor = Proveedor.objects.filter(nombre__iexact=salida.cliente.nombre).first()
    #         if not proveedor:
    #             print(f"❌ No se encontró proveedor con nombre: {salida.cliente.nombre}")
    #             return

    #         compra, _ = Compra.objects.get_or_create(
    #             numero_factura=f"TR-{salida.id}",
    #             defaults={
    #                 'orden_compra': None,
    #                 'proveedor': proveedor,
    #                 'bodega': salida.bodegaEntrada,
    #                 'observaciones': f'Traslado desde salida #{salida.id}',
    #                 'total': Decimal('0.00'),
    #                 'fecha_compra': timezone.localtime().date(),
    #                 'usuario_creador': usuario
    #             }
    #         )

    #         ItemCompra.objects.create(
    #             compra=compra,
    #             producto=producto,
    #             cantidad_recibida=cantidad,
    #             precio_unitario=Decimal('0.00')
    #         )

    # 🧮 Actualizar stock total
    stock_total = InventarioBodega.objects.filter(producto=producto).aggregate(
        total=Sum('stock')
    )['total'] or 0

    producto.stock = stock_total
    producto.save(update_fields=['stock'])