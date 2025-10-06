from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from .models import OrdenCompra, ItemOrdenCompra, Compra, ItemCompra
from django.urls import reverse
from django.http import JsonResponse
from .forms import OrdenCompraForm
from applications.productos.models import Producto
from applications.proveedores.models import Proveedor
from applications.bodegas.models import Bodega
from django.forms import modelformset_factory
from django.contrib import messages
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, IntegrityError
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils.timezone import localtime, is_naive, make_aware
from django.db.models import Q

import json

import logging

import time

logger = logging.getLogger(__name__)

@login_required(login_url='login_usuario')
def mi_vista(request):
    inicio = time.time()
    
    # tu lógica...
    response = render(request, 'mi_template.html')

    fin = time.time()
    print(f"⏱ Tiempo de respuesta del servidor: {fin - inicio:.2f} segundos")

    return response

# Create your views here.


@login_required(login_url='login_usuario')
def list_orden_y_compra(request):
    user = request.user  

    # 👉 Base querysets
    ordenes = OrdenCompra.objects.select_related('proveedor', 'usuario_creador__sucursal')
    compras = Compra.objects.select_related('orden_compra', 'proveedor', 'usuario_creador__sucursal')

    # 👉 Filtro por rol
    if user.rol in ["almacen", "empleado"]:
        if user.sucursal:  # 👈 sucursal es una Bodega
            ordenes = ordenes.filter(
                Q(usuario_creador__sucursal=user.sucursal) |
                Q(proveedor__nombre__icontains=user.sucursal.nombre)  # si usas proveedores internos con nombre = bodega
            )
            compras = compras.filter(
                Q(usuario_creador__sucursal=user.sucursal) |
                Q(bodega=user.sucursal)   # 👈 aquí va directo porque sucursal = Bodega
            )

    # -------------------------
    data = []

    # Añadir órdenes
    for orden in ordenes:
        if orden.fecha_creacion:
            fecha_dt = orden.fecha_creacion
            if is_naive(fecha_dt):
                fecha_dt = make_aware(fecha_dt)
            fecha_str = localtime(fecha_dt).strftime('%Y-%m-%dT%H:%M:%S')
        else:
            fecha_str = ''

        data.append({
            'id': orden.id,
            'proveedor': orden.proveedor.nombre if orden.proveedor else 'Sin proveedor',
            'fecha': fecha_str,
            'tipo_documento': orden.tipo_documento if hasattr(orden, 'tipo_documento') else '',
            'total': orden.total,
            'numero_factura': '',
            'estado': orden.estado,
            'usuario': (
                f"{orden.usuario_creador.get_full_name()} - {orden.usuario_creador.sucursal.nombre}"
                if orden.usuario_creador and orden.usuario_creador.sucursal else
                orden.usuario_creador.get_full_name() if orden.usuario_creador else "Sin usuario"
            ),
            'url_editar': f'/comprar_orden/{orden.id}/',
            'url_cancelar': f'/cambiar_estado_orden/{orden.id}/'
        })

    # Añadir compras
    for compra in compras:
        proveedor_nombre = 'Sin proveedor'
        if compra.orden_compra and compra.orden_compra.proveedor:
            proveedor_nombre = compra.orden_compra.proveedor.nombre
        elif compra.proveedor:
            proveedor_nombre = compra.proveedor.nombre

        if compra.fecha_compra:
            fecha_datetime = datetime.combine(compra.fecha_compra, datetime.min.time())
            if is_naive(fecha_datetime):
                fecha_datetime = make_aware(fecha_datetime)
            fecha_str = localtime(fecha_datetime).strftime('%Y-%m-%dT%H:%M:%S')
        else:
            fecha_str = ''

        data.append({
            'id': compra.id,
            'proveedor': proveedor_nombre,
            'fecha': fecha_str,
            'tipo_documento': getattr(compra, 'tipo_documento', ''),
            'total': compra.total,
            'numero_factura': compra.numero_factura or '',
            'estado': compra.estado,
            'usuario': (
                f"{compra.usuario_creador.get_full_name()} - {compra.usuario_creador.sucursal.nombre}"
                if compra.usuario_creador and compra.usuario_creador.sucursal else
                compra.usuario_creador.get_full_name() if compra.usuario_creador else "Sin usuario"
            ),
            'url_editar': f'/detalle_comprar/{compra.id}/',
            'url_cancelar': ''
        })

    return JsonResponse({'ordenes_compras': data})


#antes de roles de usuario
# @login_required(login_url='login_usuario')
# def ordenes_compra(request):
#     ordenes_compra = OrdenCompra.objects.all()
#     return render (request, 'ordenesCompra.html', {
#         'ordenes_compra': ordenes_compra
#     })
    
@login_required(login_url='login_usuario')
def ordenes_compra(request):
    user = request.user  # usuario logueado
    
    if user.rol in ["almacen", "empleado"]:
        # Filtra órdenes de usuarios que pertenezcan a la misma sucursal
        ordenes_compra = OrdenCompra.objects.filter(
            usuario_creador__sucursal=user.sucursal
        )
    else:
        # Admin (o cualquier otro rol) ve todas
        ordenes_compra = OrdenCompra.objects.all()
    
    return render(request, 'ordenesCompra.html', {
        'ordenes_compra': ordenes_compra
    })
    

  
@transaction.atomic
def crear_orden_compra(request):
    if request.method == 'POST':
        proveedor_id = request.POST.get('proveedor')
        productos = request.POST.getlist('productos[]')
        cantidades = request.POST.getlist('cantidades[]')
        precios = request.POST.getlist('precios[]')
        observaciones = request.POST.get('observacion')
        total_orden = request.POST.get('total_orden')

        # Validación temprana para proveedor y productos
        if not proveedor_id or not productos:
            messages.error(request, "Debe seleccionar un proveedor y al menos un producto.")
            return redirect('crear_orden_compra')

        # 💰 Conversión segura del total
        try:
            total_orden_decimal = Decimal(total_orden)
        except:
            total_orden_decimal = Decimal('0.00')

        try:
            proveedor = Proveedor.objects.get(id_proveedor=proveedor_id)
        except Proveedor.DoesNotExist:
            messages.error(request, "Proveedor no válido.")
            return redirect('crear_orden_compra')

        # Revisa si hay productos válidos
        productos_validos = 0  # Para contar productos con cantidad > 0
        items = []

        for i in range(len(productos)):
            try:
                cantidad = int(cantidades[i])
                precio_unitario = Decimal(precios[i].replace(',', ''))

                if cantidad > 0:  # Solo permite productos con cantidad mayor que 0
                    items.append({
                        'producto_id': productos[i],
                        'cantidad': cantidad,
                        'precio_unitario': precio_unitario
                    })
                    productos_validos += 1

            except (ValueError, IndexError, Decimal.InvalidOperation):
                continue  # Si ocurre un error, simplemente pasa al siguiente

        # Si no hay productos válidos, muestra mensaje y no crea la orden
        if productos_validos == 0:
            messages.error(request, "No se puede agregar la orden por que hay productos en Cantidad 0")
            return redirect('crear_orden_compra')

        # Si hay productos válidos, crea la orden
        orden = OrdenCompra.objects.create(
            proveedor=proveedor,
            observaciones=observaciones,
            total=total_orden_decimal,
            usuario_creador=request.user
        )

        # Ahora crea los ítems de la orden con los productos válidos
        for item in items:
            ItemOrdenCompra.objects.create(
                orden=orden,
                producto_id=item['producto_id'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio_unitario']
            )

        messages.success(request, "Orden de compra creada correctamente.")
        return redirect('ordenes_compra')

    productos = Producto.objects.all()
    return render(request, 'crearOrdenCompra.html', {'productos': productos})    
    

# View que me funcionaba
# @login_required(login_url='login_usuario')
# def comprar_orden_vista(request, orden_id):
#     orden = get_object_or_404(OrdenCompra, id=orden_id)

#     try:
#         compra = orden.compra  # usa el related_name
#     except Compra.DoesNotExist:
#         compra = None

#     items = orden.items.all()  # ajusta según tu modelo real
    
#     logger.info(f"ORDEN: {orden}")
#     logger.info(f"ESTADO: {orden.estado}")
#     logger.info(f"COMPRA: {compra}")
#     logger.info(f"ITEMS: {list(items)}")

#     return render(request, 'comprarOrden.html', {
#         'orden': orden,
#         'compra': compra,
#         'items': items,
#     })
    

# @login_required(login_url='login_usuario')
# def comprar_orden_vista(request, orden_id):
#     orden = get_object_or_404(OrdenCompra, id=orden_id)

#     try:
#         compra = orden.compra  # usa el related_name
#     except Compra.DoesNotExist:
#         compra = None

#     items = orden.items.all()  # ajusta según tu modelo real

#     # 🔹 Lógica para las bodegas
#     user = request.user
#     bodegas = None  

#     if user.rol.nombre in ['Administrador', 'Contable']:  
#         bodegas = Bodega.objects.all()
#     elif user.rol.nombre in ['Almacen', 'Empleado']:
#         # Asumiendo que usuario tiene sucursal relacionada
#         if hasattr(user, "sucursal") and user.sucursal:
#             bodegas = Bodega.objects.filter(sucursal=user.sucursal)
#         else:
#             bodegas = Bodega.objects.none()

#     logger.info(f"ORDEN: {orden}")
#     logger.info(f"ESTADO: {orden.estado}")
#     logger.info(f"COMPRA: {compra}")
#     logger.info(f"ITEMS: {list(items)}")
#     logger.info(f"BODEGAS DISPONIBLES: {list(bodegas)}")

#     return render(request, 'comprarOrden.html', {
#         'orden': orden,
#         'compra': compra,
#         'items': items,
#         'bodegas': bodegas,  # 🔹 mandamos las bodegas al template
#     })
    
   
@login_required(login_url='login_usuario')    
def detalle_comprar(request, id):
    detalle_comprar = get_object_or_404(Compra, id=id) 
    items = detalle_comprar.items.all()
    return render(request, 'compraDetalle.html', {
        'detalle_comprar': detalle_comprar,
        'items': items,
    })
    # return render (request, 'detalleCompra.html', {
    #     'detalle_comprar': comprar_orden
    # })         
    
 
@transaction.atomic
def comprar_orden(request, id):
    orden = get_object_or_404(OrdenCompra, id=id)

    if request.method == 'POST':
        # ✅ Verificar si ya existe una compra asociada
        if hasattr(orden, 'compra'):
            messages.error(request, "Esta orden ya tiene una compra registrada.")
            return redirect('ordenes_compra')

        # Obtener datos del formulario
        proveedor_id = request.POST.get('proveedor', '').strip()
        observaciones = request.POST.get('observaciones', '')
        numero_factura = request.POST.get('numFActura', '')
        bodega = request.POST.get('bodega_id')
        total = request.POST.get('total_orden')
        productos = request.POST.getlist('productos[]')
        cantidades = request.POST.getlist('cantidades[]')
        precios = request.POST.getlist('precios[]')
        fecha_compra = request.POST.getlist('fechaCompra[]')

        print(">>> Datos del formulario:")
        print("Observaciones:", observaciones)
        print("Número de factura:", numero_factura)
        print("Bodega ID:", bodega)
        print("POST completo:", dict(request.POST))  

        if not proveedor_id:
            messages.error(request, "Debe seleccionar un proveedor.")
            return redirect('comprar_orden', id=id)

        try:
            proveedor = Proveedor.objects.get(id_proveedor=proveedor_id)
        except Proveedor.DoesNotExist:
            messages.error(request, "Proveedor no válido.")
            return redirect('comprar_orden', id=id)

        # Calcular el total desde los ítems de la orden
        total_orden_decimal = sum(
            (item.cantidad * item.precio_unitario for item in orden.items.all()),
            start=Decimal('0.00')
        )
        print("Total calculado:", total_orden_decimal)
        
        # Crear la compra
        compra = Compra.objects.create(
            orden_compra=orden,
            observaciones=observaciones,
            total=total_orden_decimal,
            fecha_compra=fecha_compra,
            proveedor=proveedor,
            bodega_id=bodega if bodega else None,
            numero_factura=numero_factura,
            usuario_creador=request.user
        )

        # Crear ítems de la compra
        for i in range(len(productos)):
            producto_id = productos[i]
            cantidad = int(cantidades[i])
            precio_unitario = Decimal(precios[i].replace(',', ''))  

            ItemCompra.objects.create(
                compra=compra,
                producto_id=producto_id,
                cantidad_recibida=cantidad,
                precio_unitario=precio_unitario
            )

        # Cambiar estado de la orden
        orden.estado = 'comprada' + ' ' + compra.numero_factura
        orden.save()

        messages.success(request, "Compra registrada correctamente.")
        return redirect('ordenes_compra')
    
    # ==============================
    # GET → Preparar datos para template
    # ==============================
    try:
        compra = orden.compra  
    except Compra.DoesNotExist:
        compra = None

    items = orden.items.all()

    # 🚨 Restricción de bodegas
    if request.user.rol in ["admin", "contable"]:
        bodegas = Bodega.objects.all()
    else:
        bodegas = [request.user.sucursal]  # 👈 Solo la sucursal del usuario

    return render(request, 'comprarOrden.html', {
        'orden': orden,
        'compra': compra,
        'items': items,
        'bodegas': bodegas,   # <-- se manda al template
    })


#de nuevo comento este dejo el codigo de arriba
# @transaction.atomic
# def comprar_orden(request, id):
#     orden = get_object_or_404(OrdenCompra, id=id)

#     if request.method == 'POST':
#         # ✅ Verificar si ya existe una compra asociada
#         if hasattr(orden, 'compra'):
#             messages.error(request, "Esta orden ya tiene una compra registrada.")
#             return redirect('ordenes_compra')

#         # Obtener datos del formulario
#         proveedor_id = request.POST.get('proveedor', '').strip()
#         observaciones = request.POST.get('observaciones', '')
#         numero_factura = request.POST.get('numFActura', '')
#         bodega = request.POST.get('bodega_id')
#         total = request.POST.get('total_orden')
#         productos = request.POST.getlist('productos[]')
#         cantidades = request.POST.getlist('cantidades[]')
#         precios = request.POST.getlist('precios[]')
#         fecha_compra = request.POST.getlist('fechaCompra[]')

#         print(">>> Datos del formulario:")
#         print("Observaciones:", observaciones)
#         print("Número de factura:", numero_factura)
#         print("Bodega ID:", bodega)
#         print("POST completo:", dict(request.POST))  

#         if not proveedor_id:
#             messages.error(request, "Debe seleccionar un proveedor.")
#             return redirect('comprar_orden', id=id)

#         try:
#             proveedor = Proveedor.objects.get(id_proveedor=proveedor_id)
#         except Proveedor.DoesNotExist:
#             messages.error(request, "Proveedor no válido.")
#             return redirect('comprar_orden', id=id)

#         # Calcular el total desde los ítems de la orden
#         total_orden_decimal = sum(
#             (item.cantidad * item.precio_unitario for item in orden.items.all()),
#             start=Decimal('0.00')
#         )
#         print("Total calculado:", total_orden_decimal)
        
#         # Crear la compra
#         compra = Compra.objects.create(
#             orden_compra=orden,
#             observaciones=observaciones,
#             total=total,
#             fecha_compra=fecha_compra,
#             proveedor=proveedor,
#             bodega_id=bodega if bodega else None,
#             numero_factura=numero_factura,
#             usuario_creador=request.user
#         )

#         # Crear ítems de la compra
#         for i in range(len(productos)):
#             producto_id = productos[i]
#             cantidad = int(cantidades[i])
#             precio_unitario = Decimal(precios[i].replace(',', ''))  

#             ItemCompra.objects.create(
#                 compra=compra,
#                 producto_id=producto_id,
#                 cantidad_recibida=cantidad,
#                 precio_unitario=precio_unitario
#             )

#         # Cambiar estado de la orden
#         orden.estado = 'comprada' + ' ' + compra.numero_factura
#         orden.save()

#         messages.success(request, "Compra registrada correctamente.")
#         return redirect('ordenes_compra')
    
#     # ==============================
#     # GET → Preparar datos para template
#     # ==============================
#     try:
#         compra = orden.compra  
#     except Compra.DoesNotExist:
#         compra = None

#     items = orden.items.all()

#    # 🚨 Restricción de bodegas
#     if request.user.rol in ["admin", "contable"]:   # Usamos tu campo 'rol'
#         bodegas = Bodega.objects.all()
#     else:
#         bodegas = Bodega.objects.filter(id=request.user.sucursal_id)  # 👈 solo la sucursal asignada

#     return render(request, 'comprarOrden.html', {
#         'orden': orden,
#         'compra': compra,
#         'items': items,
#         'bodegas': bodegas,   # <-- se manda al template
#     })    

    
#codigo comentado para probar el que dejo arriba
# @transaction.atomic
# def comprar_orden(request, id):
#     orden = get_object_or_404(OrdenCompra, id=id)

#     if request.method == 'POST':
#         # ✅ Verificar si ya existe una compra asociada
#         if hasattr(orden, 'compra'):
#             messages.error(request, "Esta orden ya tiene una compra registrada.")
#             return redirect('ordenes_compra')

#         # Obtener datos del formulario
#         proveedor_id = request.POST.get('proveedor', '').strip()
#         observaciones = request.POST.get('observaciones', '')
#         numero_factura = request.POST.get('numFActura', '')
#         bodega = request.POST.get('bodega_id')
#         total = request.POST.get('total_orden')
#         productos = request.POST.getlist('productos[]')
#         cantidades = request.POST.getlist('cantidades[]')
#         precios = request.POST.getlist('precios[]')
#         fecha_compra = request.POST.getlist('fechaCompra[]')

#         # 📌 Imprimir datos recibidos como depuración (tipo var_dump)
#         print(">>> Datos del formulario:")
#         print("Observaciones:", observaciones)
#         print("Número de factura:", numero_factura)
#         print("Bodega ID:", bodega)
#         print("POST completo:", dict(request.POST))  # También puedes usar request.POST.items()
        
#         if not proveedor_id:
#             messages.error(request, "Debe seleccionar un proveedor.")
#             return redirect('comprar_orden', id=id)

#         try:
#             proveedor = Proveedor.objects.get(id_proveedor=proveedor_id)
#         except Proveedor.DoesNotExist:
#             messages.error(request, "Proveedor no válido.")
#             return redirect('comprar_orden', id=id)




#         # Calcular el total
#         total_orden_decimal = sum(
#             (item.cantidad * item.precio_unitario for item in orden.items.all()),
#             start=Decimal('0.00')
#         )
#         print("Total calculado:", total_orden_decimal)
        
#         # Crear la compra
#         compra = Compra.objects.create(
#             orden_compra=orden,
#             observaciones=observaciones,
#             total=total,
#             fecha_compra = fecha_compra,
#             proveedor=proveedor,
#             bodega_id=bodega if bodega else None,
#             numero_factura=numero_factura,
#             usuario_creador=request.user
#         )

#         # Crear los ítems de la compra
#         # for item in orden.items.all():
#         #     ItemCompra.objects.create(
#         #         compra=compra,
#         #         producto=item.producto,
#         #         cantidad_recibida=item.cantidad,
#         #         precio_unitario=item.precio_unitario
#         #     )
#         for i in range(len(productos)):
#             producto_id = productos[i]
#             cantidad = int(cantidades[i])
#             precio_unitario = Decimal(precios[i].replace(',', ''))  # limpia el formato si viene con comas

#             ItemCompra.objects.create(
#                 compra=compra,
#                 producto_id=producto_id,
#                 cantidad_recibida=cantidad,
#                 precio_unitario=precio_unitario
#             )

#         # Cambia el estado de la orden a "comprada"
#         orden.estado = 'comprada' + ' ' + compra.numero_factura
#         orden.save()

#         messages.success(request, "Compra registrada correctamente.")
#         return redirect('ordenes_compra')
    
#     try:
#         compra = orden.compra  # usa el related_name
#     except Compra.DoesNotExist:
#         compra = None

#     items = orden.items.all()  # ajusta según tu modelo real
    
   
#     return render(request, 'comprarOrden.html', {
#         'orden': orden,
#         'compra': compra,
#         'items': items,
#     })

    # return render(request, 'comprarOrden.html', {
    #     'orden': orden,
    #     'items': orden.items.all()
    # }) 
   

@transaction.atomic
def confirmar_compra(request, orden_id):
    orden = get_object_or_404(OrdenCompra, id=orden_id)

    # Verifica que la orden no esté ya comprada
    if orden.estado == 'comprada':
        messages.warning(request, "Esta orden ya fue confirmada como compra.")
        return redirect('comprar_orden_vista', id=orden.id)

    # Crea la compra
    compra = Compra.objects.create(
        orden_compra=orden,
        observaciones=orden.observaciones
    )

    # Copia los ítems de la orden a la compra y actualiza el inventario
    for item in orden.items.all():
        ItemCompra.objects.create(
            compra=compra,
            producto=item.producto,
            cantidad_recibida=item.cantidad,
            precio_unitario=item.precio_unitario
        )
        # Actualiza stock del producto
        producto = item.producto
        producto.stock += item.cantidad
        producto.save()

    # Cambia el estado de la orden a "comprada"
    orden.estado = 'comprada'
    orden.save()

    messages.success(request, "Compra registrada exitosamente y stock actualizado.")
    return redirect('comprar_orden_vista', id=orden.id)        


@csrf_exempt  # si usas fetch sin enviar el CSRF token
def cambiar_estado_orden(request, orden_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nuevo_estado = data.get('estado')
            
            orden = OrdenCompra.objects.get(pk=orden_id)
            orden.estado = nuevo_estado
            orden.save()
            
            return JsonResponse({'success': True})
        except OrdenCompra.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Orden no encontrada'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)