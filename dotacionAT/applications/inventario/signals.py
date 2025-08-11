# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.utils import timezone
# from django.db.models import Sum

# from applications.ordenes_compra.models import ItemCompra, Compra
# from applications.ordenes_salida.models import ItemSalida
# from applications.productos.models import Producto
# from dotacionAT.middleware import get_current_user

# # 🟢 Entrada por compra
# @receiver(post_save, sender=ItemCompra)
# def actualizar_inventario_y_producto(sender, instance, created, **kwargs):
    
#     usuario = get_current_user()
    
#     if created and instance.compra.bodega:
#         inventario, _ = InventarioBodega.objects.get_or_create(
#             bodega=instance.compra.bodega,
#             producto=instance.producto
#         )
        
#         cantidad = instance.cantidad_recibida or 0
#         inventario.entradas += cantidad
#         inventario.stock += cantidad
#         inventario.ultima_entrada = timezone.now()
#         inventario.usuario_ultima_entrada=usuario
#         inventario.save()

#         print(f"✅ Inventario actualizado para: {instance.producto.nombre} en {instance.compra.bodega.nombre}")

#         # Actualizar el costo del producto
#         producto = instance.producto
#         producto.costo = instance.precio_unitario
#         producto.save(update_fields=['costo'])

#         # Actualizar stock total del producto en todas las bodegas
#         stock_total = InventarioBodega.objects.filter(producto=producto).aggregate(
#             total=Sum('stock')
#         )['total'] or 0

#         producto.stock = stock_total
#         producto.save(update_fields=['stock'])

# # 🔴 Salida de productos y traslado entre bodegas
# @receiver(post_save, sender=ItemSalida)
# def actualizar_inventario_salida(sender, instance, created, **kwargs):
    
#     usuario = get_current_user()
    
#     if not created:
#         return

#     producto = instance.producto
#     cantidad = instance.cantidad or 0
#     salida = instance.salida

#     if cantidad <= 0 or not producto:
#         return

#     # 1. Salida de la bodega origen
#     if salida.bodegaSalida:
#         inventario_salida, _ = InventarioBodega.objects.get_or_create(
#             bodega=salida.bodegaSalida,
#             producto=producto
#         )
#         inventario_salida.salidas += cantidad
#         inventario_salida.stock -= cantidad
#         inventario_salida.ultima_salida = timezone.now()
#         inventario_salida.usuario_ultima_salida=usuario
#         inventario_salida.save()
#         print(f"📤 Producto '{producto.nombre}' salido de {salida.bodegaSalida.nombre}: -{cantidad}")

#     # 2. Entrada a la bodega destino (si aplica)
#     if salida.bodegaEntrada:
#         inventario_entrada, _ = InventarioBodega.objects.get_or_create(
#             bodega=salida.bodegaEntrada,
#             producto=producto
#         )
#         inventario_entrada.entradas += cantidad
#         inventario_entrada.stock += cantidad
#         inventario_entrada.ultima_entrada = timezone.now()
#         inventario_entrada.usuario_ultima_entrada=usuario
#         inventario_entrada.save()
#         print(f"📥 Producto '{producto.nombre}' recibido en {salida.bodegaEntrada.nombre}: +{cantidad}")

#     # 3. Actualizar stock total del producto en todas las bodegas
#     stock_total = InventarioBodega.objects.filter(producto=producto).aggregate(
#         total=Sum('stock')
#     )['total'] or 0

#     producto.stock = stock_total
#     producto.save(update_fields=['stock'])

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.utils import timezone
# from django.db.models import Sum
# from django.db import transaction

# from .models import InventarioBodega
# from applications.ordenes_compra.models import ItemCompra, Compra
# from applications.ordenes_salida.models import ItemSalida
# from applications.productos.models import Producto
# from dotacionAT.middleware import get_current_user


# # 🟢 Entrada por compra (clásica)
# @receiver(post_save, sender=ItemCompra)
# def actualizar_inventario_y_producto(sender, instance, created, **kwargs):
#     usuario = get_current_user()

#     if created and instance.compra.bodega:
#         inventario, _ = InventarioBodega.objects.get_or_create(
#             bodega=instance.compra.bodega,
#             producto=instance.producto
#         )

#         cantidad = instance.cantidad_recibida or 0
#         inventario.entradas += cantidad
#         inventario.stock += cantidad
#         inventario.ultima_entrada = timezone.now()
#         inventario.usuario_ultima_entrada = usuario
#         inventario.save()

#         print(f"✅ Inventario actualizado para: {instance.producto.nombre} en {instance.compra.bodega.nombre}")

#         # Actualizar costo del producto
#         producto = instance.producto
#         producto.costo = instance.precio_unitario
#         producto.save(update_fields=['costo'])

#         # Stock total del producto en todas las bodegas
#         stock_total = InventarioBodega.objects.filter(producto=producto).aggregate(
#             total=Sum('stock')
#         )['total'] or 0
#         producto.stock = stock_total
#         producto.save(update_fields=['stock'])


# # 🔴 Salida de productos y traslado entre bodegas
# @receiver(post_save, sender=ItemSalida)
# @transaction.atomic
# def actualizar_inventario_salida(sender, instance, created, **kwargs):
#     usuario = get_current_user()

#     if not created:
#         return

#     producto = instance.producto
#     cantidad = instance.cantidad or 0
#     salida = instance.salida

#     if cantidad <= 0 or not producto:
#         return

#     # 1. Salida de la bodega origen
#     if salida.bodegaSalida:
#         inventario_salida, _ = InventarioBodega.objects.get_or_create(
#             bodega=salida.bodegaSalida,
#             producto=producto
#         )
#         inventario_salida.salidas += cantidad
#         inventario_salida.stock -= cantidad
#         inventario_salida.ultima_salida = timezone.now()
#         inventario_salida.usuario_ultima_salida = usuario
#         inventario_salida.save()
#         print(f"📤 Producto '{producto.nombre}' salido de {salida.bodegaSalida.nombre}: -{cantidad}")

#     # 2. Entrada a la bodega destino (si aplica)
#     if salida.bodegaEntrada:
#         inventario_entrada, _ = InventarioBodega.objects.get_or_create(
#             bodega=salida.bodegaEntrada,
#             producto=producto
#         )
#         inventario_entrada.entradas += cantidad
#         inventario_entrada.stock += cantidad
#         inventario_entrada.ultima_entrada = timezone.now()
#         inventario_entrada.usuario_ultima_entrada = usuario
#         inventario_entrada.save()
#         print(f"📥 Producto '{producto.nombre}' recibido en {salida.bodegaEntrada.nombre}: +{cantidad}")

#         # ✅ Registrar como compra interna si es traslado
#         if salida.tipo_documento == 'TR':
#             compra, creada = Compra.objects.get_or_create(
#                 orden_compra=None,
#                 bodega=salida.bodegaEntrada,
#                 proveedor=None,  # Ajusta si necesitas proveedor "interno"
#                 numero_factura=f'TR-{salida.id}',
#                 defaults={
#                     'observaciones': f'Traslado desde {salida.bodegaSalida.nombre}',
#                     'estado': 'Traslado',
#                     'total': 0,
#                     'usuario_creador': usuario,
#                 }
#             )

#             ItemCompra.objects.create(
#                 compra=compra,
#                 producto=producto,
#                 cantidad_recibida=cantidad,
#                 precio_unitario=producto.costo or 0  # Puedes ajustar este valor
#             )
#             print(f"📝 Compra interna registrada en {salida.bodegaEntrada.nombre} por traslado.")

#     # 3. Actualizar stock total del producto
#     stock_total = InventarioBodega.objects.filter(producto=producto).aggregate(
#         total=Sum('stock')
#     )['total'] or 0

#     producto.stock = stock_total
#     producto.save(update_fields=['stock'])



# from .models import InventarioBodega
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.utils import timezone
# from django.db.models import Sum
# from decimal import Decimal

# from applications.ordenes_compra.models import ItemCompra, Compra
# from applications.ordenes_salida.models import ItemSalida
# from applications.productos.models import Producto
# from dotacionAT.middleware import get_current_user
# from applications.bodegas.models import Bodega

# @receiver(post_save, sender=ItemCompra)
# def actualizar_inventario_y_producto(sender, instance, created, **kwargs):
#     usuario = get_current_user()

#     if created and instance.compra.bodega:
#         inventario, _ = InventarioBodega.objects.get_or_create(
#             bodega=instance.compra.bodega,
#             producto=instance.producto
#         )

#         cantidad = instance.cantidad_recibida or 0
#         inventario.entradas += cantidad
#         inventario.stock += cantidad
#         inventario.ultima_entrada = timezone.now()
#         inventario.usuario_ultima_entrada = usuario
#         inventario.save()

#         producto = instance.producto
#         producto.costo = instance.precio_unitario
#         producto.save(update_fields=['costo'])

#         stock_total = InventarioBodega.objects.filter(producto=producto).aggregate(
#             total=Sum('stock')
#         )['total'] or 0

#         producto.stock = stock_total
#         producto.save(update_fields=['stock'])


# @receiver(post_save, sender=ItemSalida)
# def actualizar_inventario_salida(sender, instance, created, **kwargs):
#     usuario = get_current_user()

#     if not created:
#         return

#     producto = instance.producto
#     cantidad = instance.cantidad or 0
#     salida = instance.salida

#     if cantidad <= 0 or not producto:
#         return

#     if salida.bodegaSalida:
#         inventario_salida, _ = InventarioBodega.objects.get_or_create(
#             bodega=salida.bodegaSalida,
#             producto=producto
#         )
#         inventario_salida.salidas += cantidad
#         inventario_salida.stock -= cantidad
#         inventario_salida.ultima_salida = timezone.now()
#         inventario_salida.usuario_ultima_salida = usuario
#         inventario_salida.save()

#     if salida.bodegaEntrada:
#         inventario_entrada, _ = InventarioBodega.objects.get_or_create(
#             bodega=salida.bodegaEntrada,
#             producto=producto
#         )
#         inventario_entrada.entradas += cantidad
#         inventario_entrada.stock += cantidad
#         inventario_entrada.ultima_entrada = timezone.now()
#         inventario_entrada.usuario_ultima_entrada = usuario
#         inventario_entrada.save()

#         if salida.tipo_documento == 'TR':
#             compra, creada = Compra.objects.get_or_create(
#                 numero_factura=f"TR-{salida.id}",
#                 defaults={
#                     'orden_compra': None,
#                     'proveedor': salida.cliente,
#                     'bodega': salida.bodegaEntrada,
#                     'observaciones': f'Traslado desde salida #{salida.id}',
#                     'total': Decimal('0.00'),
#                     'fecha_compra': timezone.now().date(),
#                     'usuario_creador': usuario
#                 }
#             )

#             ItemCompra.objects.create(
#                 compra=compra,
#                 producto=producto,
#                 cantidad_recibida=cantidad,
#                 precio_unitario=Decimal('0.00')
#             )

#     stock_total = InventarioBodega.objects.filter(producto=producto).aggregate(
#         total=Sum('stock')
#     )['total'] or 0

#     producto.stock = stock_total
#     producto.save(update_fields=['stock'])


# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.utils import timezone
# from django.db.models import Sum
# from decimal import Decimal

# from .models import InventarioBodega
# from applications.ordenes_compra.models import ItemCompra, Compra, Proveedor
# from applications.ordenes_salida.models import ItemSalida
# from applications.productos.models import Producto
# from dotacionAT.middleware import get_current_user



# # ✅ Entrada por compra
# @receiver(post_save, sender=ItemCompra)
# def actualizar_inventario_y_producto(sender, instance, created, **kwargs):
#     usuario = get_current_user()

#     if created and instance.compra.bodega:
#         inventario, _ = InventarioBodega.objects.get_or_create(
#             bodega=instance.compra.bodega,
#             producto=instance.producto
#         )

#         cantidad = instance.cantidad_recibida or 0
#         inventario.entradas += cantidad
#         inventario.stock += cantidad
#         inventario.ultima_entrada = timezone.now()
#         inventario.usuario_ultima_entrada = usuario
#         inventario.save()

#         producto = instance.producto
#         producto.costo = instance.precio_unitario
#         producto.save(update_fields=['costo'])

#         stock_total = InventarioBodega.objects.filter(producto=producto).aggregate(
#             total=Sum('stock')
#         )['total'] or 0

#         producto.stock = stock_total
#         producto.save(update_fields=['stock'])


# # 🔁 Salida y traslado entre bodegas
# @receiver(post_save, sender=ItemSalida)
# def actualizar_inventario_salida(sender, instance, created, **kwargs):
#     usuario = get_current_user()

#     if not created:
#         return

#     producto = instance.producto
#     cantidad = instance.cantidad or 0
#     salida = instance.salida

#     if cantidad <= 0 or not producto:
#         return

#     # 🟢 Salida desde bodega origen
#     if salida.bodegaSalida:
#         inventario_salida, _ = InventarioBodega.objects.get_or_create(
#             bodega=salida.bodegaSalida,
#             producto=producto
#         )
#         inventario_salida.salidas += cantidad
#         inventario_salida.stock -= cantidad
#         inventario_salida.ultima_salida = timezone.now()
#         inventario_salida.usuario_ultima_salida = usuario
#         inventario_salida.save()

#     # 🔵 Entrada a bodega destino
#     if salida.bodegaEntrada:
#         inventario_entrada, _ = InventarioBodega.objects.get_or_create(
#             bodega=salida.bodegaEntrada,
#             producto=producto
#         )
#         inventario_entrada.entradas += cantidad
#         inventario_entrada.stock += cantidad
#         inventario_entrada.ultima_entrada = timezone.now()
#         inventario_entrada.usuario_ultima_entrada = usuario
#         inventario_entrada.save()

#         # 🧾 Si es un TRASLADO, crear Compra automáticamente
#         if salida.tipo_documento == 'TR':
#             # Buscar proveedor con mismo nombre que el cliente
#             proveedor = Proveedor.objects.filter(nombre__iexact=salida.cliente.nombre).first()
#             if not proveedor:
#                 print(f"❌ No se encontró proveedor con nombre: {salida.cliente.nombre}")
#                 return  # No crear compra si no hay proveedor válido

#             # Crear la Compra si no existe
#             compra, creada = Compra.objects.get_or_create(
#                 numero_factura=f"TR-{salida.id}",
#                 defaults={
#                     'orden_compra': None,
#                     'proveedor': proveedor,
#                     'bodega': salida.bodegaEntrada,
#                     'observaciones': f'Traslado desde salida #{salida.id}',
#                     'total': Decimal('0.00'),
#                     'fecha_compra': timezone.localtime().date(),
#                     'usuario_creador': usuario
#                 }
#             )

#             # Crear el ItemCompra
#             ItemCompra.objects.create(
#                 compra=compra,
#                 producto=producto,
#                 cantidad_recibida=cantidad,
#                 precio_unitario=Decimal('0.00')
#             )

#     # 🧮 Actualizar stock total
#     stock_total = InventarioBodega.objects.filter(producto=producto).aggregate(
#         total=Sum('stock')
#     )['total'] or 0

#     producto.stock = stock_total
#     producto.save(update_fields=['stock'])


# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.utils import timezone
# from django.db.models import Sum
# from decimal import Decimal

# from .models import InventarioBodega
# from applications.ordenes_compra.models import ItemCompra, Compra, Proveedor
# from applications.ordenes_salida.models import ItemSalida
# from applications.productos.models import Producto
# from dotacionAT.middleware import get_current_user


# # ✅ Entrada por compra
# @receiver(post_save, sender=ItemCompra)
# def actualizar_inventario_y_producto(sender, instance, created, **kwargs):
#     usuario = get_current_user()

#     if created and instance.compra.bodega:
#         inventario, _ = InventarioBodega.objects.get_or_create(
#             bodega=instance.compra.bodega,
#             producto=instance.producto
#         )

#         cantidad = instance.cantidad_recibida or 0
#         inventario.entradas += cantidad
#         inventario.stock += cantidad
#         inventario.ultima_entrada = timezone.now()
#         inventario.usuario_ultima_entrada = usuario
#         inventario.save()

#         producto = instance.producto
#         producto.costo = instance.precio_unitario
#         producto.save(update_fields=['costo'])

#         stock_total = InventarioBodega.objects.filter(producto=producto).aggregate(
#             total=Sum('stock')
#         )['total'] or 0

#         producto.stock = stock_total
#         producto.save(update_fields=['stock'])


# # 🔁 Salida y traslado entre bodegas
# @receiver(post_save, sender=ItemSalida)
# def actualizar_inventario_salida(sender, instance, created, **kwargs):
#     if not created:
#         return

#     producto = instance.producto
#     cantidad = instance.cantidad or 0
#     salida = instance.salida

#     if cantidad <= 0 or not producto:
#         return

#     # 🔐 Obtener usuario desde la salida o el middleware
#     usuario = salida.usuario_creador or get_current_user()

#     # 🟢 Salida desde bodega origen
#     if salida.bodegaSalida:
#         inventario_salida, _ = InventarioBodega.objects.get_or_create(
#             bodega=salida.bodegaSalida,
#             producto=producto
#         )
#         inventario_salida.salidas += cantidad
#         inventario_salida.stock -= cantidad
#         inventario_salida.ultima_salida = timezone.now()
#         inventario_salida.usuario_ultima_salida = usuario
#         inventario_salida.save()

#     # 🔵 Entrada a bodega destino
#     if salida.bodegaEntrada:
#         inventario_entrada, _ = InventarioBodega.objects.get_or_create(
#             bodega=salida.bodegaEntrada,
#             producto=producto
#         )
#         inventario_entrada.entradas += cantidad
#         inventario_entrada.stock += cantidad
#         inventario_entrada.ultima_entrada = timezone.now()
#         inventario_entrada.usuario_ultima_entrada = usuario
#         inventario_entrada.save()

#         # 🧾 Si es un TRASLADO, crear Compra automáticamente
#         if salida.tipo_documento == 'TR':
#             proveedor = Proveedor.objects.filter(nombre__iexact=salida.cliente.nombre).first()
#             if not proveedor:
#                 print(f"❌ No se encontró proveedor con nombre: {salida.cliente.nombre}")
#                 return

#             compra, _ = Compra.objects.get_or_create(
#                 numero_factura=f"TR-{salida.id}",
#                 defaults={
#                     'orden_compra': None,
#                     'proveedor': proveedor,
#                     'bodega': salida.bodegaEntrada,
#                     'observaciones': f'Traslado desde salida #{salida.id}',
#                     'total': Decimal('0.00'),
#                     'fecha_compra': timezone.localtime().date(),
#                     'usuario_creador': usuario
#                 }
#             )

#             ItemCompra.objects.create(
#                 compra=compra,
#                 producto=producto,
#                 cantidad_recibida=cantidad,
#                 precio_unitario=Decimal('0.00')
#             )

#     # 🧮 Actualizar stock total
#     stock_total = InventarioBodega.objects.filter(producto=producto).aggregate(
#         total=Sum('stock')
#     )['total'] or 0

#     producto.stock = stock_total
#     producto.save(update_fields=['stock'])


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
    if salida.bodegaEntrada:
        inventario_entrada, _ = InventarioBodega.objects.get_or_create(
            bodega=salida.bodegaEntrada,
            producto=producto
        )
        inventario_entrada.entradas += cantidad
        inventario_entrada.stock += cantidad
        inventario_entrada.ultima_entrada = timezone.now()
        inventario_entrada.usuario_ultima_entrada = usuario
        inventario_entrada.save()

        # 🧾 Si es un TRASLADO, crear Compra automáticamente
        if salida.tipo_documento == 'TR':
            proveedor = Proveedor.objects.filter(nombre__iexact=salida.cliente.nombre).first()
            if not proveedor:
                print(f"❌ No se encontró proveedor con nombre: {salida.cliente.nombre}")
                return

            compra, _ = Compra.objects.get_or_create(
                numero_factura=f"TR-{salida.id}",
                defaults={
                    'orden_compra': None,
                    'proveedor': proveedor,
                    'bodega': salida.bodegaEntrada,
                    'observaciones': f'Traslado desde salida #{salida.id}',
                    'total': Decimal('0.00'),
                    'fecha_compra': timezone.localtime().date(),
                    'usuario_creador': usuario
                }
            )

            ItemCompra.objects.create(
                compra=compra,
                producto=producto,
                cantidad_recibida=cantidad,
                precio_unitario=Decimal('0.00')
            )

    # 🧮 Actualizar stock total
    stock_total = InventarioBodega.objects.filter(producto=producto).aggregate(
        total=Sum('stock')
    )['total'] or 0

    producto.stock = stock_total
    producto.save(update_fields=['stock'])