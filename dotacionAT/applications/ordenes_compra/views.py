from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from .models import OrdenCompra, ItemOrdenCompra, Compra, ItemCompra
from django.urls import reverse
from django.http import JsonResponse
from .forms import OrdenCompraForm
from applications.productos.models import Producto
from applications.proveedores.models import Proveedor
from django.forms import modelformset_factory
from django.contrib import messages
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, IntegrityError

import json

import logging

import time


logger = logging.getLogger(__name__)

def mi_vista(request):
    inicio = time.time()
    
    # tu lógica...
    response = render(request, 'mi_template.html')

    fin = time.time()
    print(f"⏱ Tiempo de respuesta del servidor: {fin - inicio:.2f} segundos")

    return response

# Create your views here.

# def list_orden_compra(_request):
#     # orden_compra =list(OrdenCompra.objects.values())
#     # data={'orden_compra':orden_compra}
#     # return JsonResponse(data)
#     orden_compras = OrdenCompra.objects.all()
#     data = {
#         'orden_compra': [
#             {
#                 'id': orden_compra.id,
#                 'proveedor': orden_compra.proveedor.nombre,
#                 'estado': orden_compra.estado,                
#                 'fecha': orden_compra.fecha_creacion,
#                 'observacion': orden_compra.observaciones,
#                 'url_editar': reverse('comprar_orden', args=[orden_compra.id])
#             } for orden_compra in orden_compras
#         ]
#     }
#     return JsonResponse(data)


# def list_compra(request):
#     compras = Compra.objects.select_related('orden_compra', 'orden_compra__proveedor').prefetch_related('items')

#     data = {
#         'compras': [
#             {
#                 'id': compra.id,
#                 'orden_id': compra.orden_compra.id,
#                 'proveedor': compra.orden_compra.proveedor.nombre,
#                 'fecha_recepcion': compra.fecha_recepcion.strftime('%Y-%m-%d'),
#                 'observaciones': compra.observaciones,
#                 'items': [
#                     {
#                         'producto': item.producto.nombre,
#                         'cantidad_recibida': item.cantidad_recibida,
#                         'precio_unitario': float(item.precio_unitario),
#                         'subtotal': float(item.subtotal())
#                     } for item in compra.items.all()
#                 ]
#             }
#             for compra in compras
#         ]
#     }

#     return JsonResponse(data)


def list_orden_y_compra(request):
    ordenes = OrdenCompra.objects.select_related('proveedor')
    compras = Compra.objects.select_related('orden_compra__proveedor')

    data = []

    # Añadir órdenes
    for orden in ordenes:
        data.append({
            'id': orden.id,
            'proveedor': orden.proveedor.nombre,
            'fecha': orden.fecha_creacion.strftime('%Y-%m-%d'),
            'tipo_documento': orden.tipo_documento,
            'total': orden.total,
            'numero_factura': '',
            'estado': orden.estado,
            'url_editar': f'/comprar_orden/{orden.id}/',
            'url_cancelar': f'/cambiar_estado_orden/{orden.id}/'
        })

    # Añadir compras
    for compra in compras:
        data.append({
            'id': compra.id,
            'proveedor': compra.orden_compra.proveedor.nombre,
            'fecha': compra.fecha_compra.strftime('%Y-%m-%d'),
            'tipo_documento': compra.tipo_documento,
            'total': compra.total,
            'numero_factura': compra.numero_factura,
            'estado': compra.estado,
            'url_editar': f'/detalle_comprar/{compra.id}/',
            'url_cancelar':''
        })

    return JsonResponse({'ordenes_compras': data})


def ordenes_compra(request):
    ordenes_compra = OrdenCompra.objects.all()
    return render (request, 'ordenesCompra.html', {
        'ordenes_compra': ordenes_compra
    })
    
    
# def crear_orden_compra(request):
#     if request.method == 'POST':
#         form = OrdenCompraForm(request.POST)
#         if form.is_valid():
#             orden = form.save()
#             productos = request.POST.getlist('productos[]')
#             cantidades = request.POST.getlist('cantidades[]')
#             precios = request.POST.getlist('precios[]')

#             for i in range(len(productos)):
#                 ItemOrdenCompra.objects.create(
#                     orden=orden,
#                     producto_id=productos[i],
#                     cantidad=cantidades[i],
#                     precio_unitario=precios[i]
#                 )
#             return redirect('ordenes_compra')

#     else:
#         form = OrdenCompraForm()

#     productos = Producto.objects.all()
#     return render(request, 'crearOrdenCompra.html', {
#         'form': form,
#         'productos': productos
#     })
# @transaction.atomic
# def crear_orden_compra(request):
    
  
    
    
#     if request.method == 'POST':
#         print("Token recibido:", request.POST.get("csrfmiddlewaretoken"))
#         proveedor_id = request.POST.get('proveedor')
#         observaciones = request.POST.get('observacion')
#         total_orden = request.POST.get('total_orden')
        
#         productos = request.POST.getlist('productos[]')

#         # ✅ Validación temprana DENTRO del POST
#         if not proveedor_id or not productos:
#             messages.error(request, "Debe seleccionar un proveedor y al menos un producto.")
#             return redirect('crear_orden_compra')
       

#         # 💰 Conversión de total
       
#         try:
#             total_orden_decimal = Decimal(total_orden)
#         except:
#             total_orden_decimal = Decimal('0.00')

#         if proveedor_id:
#             proveedor = Proveedor.objects.get(id_proveedor=proveedor_id)

#             # Guarda el total si tu modelo OrdenCompra tiene un campo para esto
#             orden = OrdenCompra.objects.create(
#                 proveedor=proveedor,
#                 observaciones=observaciones,
#                 total=total_orden_decimal  # <- este campo debe existir en tu modelo
#             )

#             productos = request.POST.getlist('productos[]')
#             cantidades = request.POST.getlist('cantidades[]')
#             precios = request.POST.getlist('precios[]')
            
            
     

#             for i in range(len(productos)):
                
                
                
                
                
#                 ItemOrdenCompra.objects.create(
#                     orden=orden,
#                     producto_id=productos[i],
#                     cantidad=cantidades[i],
#                     precio_unitario=precios[i]
#                 )

#             messages.success(request, "Orden Compra Creada Correctamente. ! ")    
#             return redirect('ordenes_compra')

#     productos = Producto.objects.all()
#     return render(request, 'crearOrdenCompra.html', {
#         'productos': productos
#     })
    
    
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
            total=total_orden_decimal
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
    
# def comprar_orden_vista(request):
#     comprar_orden = OrdenCompra.objects.all()
#     return render (request, 'comprarOrden.html', {
#         'comprar_orden': comprar_orden
#     })

def comprar_orden_vista(request, orden_id):
    orden = get_object_or_404(OrdenCompra, id=orden_id)

    try:
        compra = orden.compra  # usa el related_name
    except Compra.DoesNotExist:
        compra = None

    items = orden.items.all()  # ajusta según tu modelo real
    
    logger.info(f"ORDEN: {orden}")
    logger.info(f"ESTADO: {orden.estado}")
    logger.info(f"COMPRA: {compra}")
    logger.info(f"ITEMS: {list(items)}")

    return render(request, 'comprarOrden.html', {
        'orden': orden,
        'compra': compra,
        'items': items,
    })
    
    
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
    
    
# def comprar_orden(request, id):
#     orden = get_object_or_404(OrdenCompra, id=id)
#     items = orden.items.all()  # gracias al related_name='items' en el modelo

#     return render(request, 'comprarOrden.html', {
#         'orden': orden,
#         'items': items,
#     })
    
    
# @transaction.atomic
# def comprar_orden(request, id):
#     orden = get_object_or_404(OrdenCompra, id=id)

#     if request.method == 'POST':
#         print(">>> POST recibido: procesando compra")  # Este debe aparecer en tu consola

#         # Crear compra relacionada con la orden
#         compra = Compra.objects.create(
#              orden_compra=orden,
#              observaciones=observaciones,
#              total=total_orden_decimal,
#              bodega_id=bodega if bodega else None,
#              numero_factura=numero_factura
#         )
#         print(f">>> Compra creada con ID: {compra.id}")

#         # Crear los items de la compra copiando los de la orden
#         for item in orden.items.all():
#             ItemCompra.objects.create(
#                 compra=compra,
#                 producto=item.producto,
#                 cantidad_recibida=item.cantidad,
#                 precio_unitario=item.precio_unitario
#             )
#             print(f">>> ItemCompra creado para producto: {item.producto.nombre}")

#         return redirect('list_orden_y_compra')

#     print(">>> GET recibido: mostrando formulario")  # Verifica que entra en GET también
#     return render(request, 'comprarOrden.html', {
#         'orden': orden,
#         'items': orden.items.all()
#     })

# @transaction.atomic
# def comprar_orden(request, id):
#     orden = get_object_or_404(OrdenCompra, id=id)

#     if request.method == 'POST':
#         print(">>> POST recibido: procesando compra")  # Este debe aparecer en tu consola

#         # 🔽 OBTENER LOS CAMPOS DEL FORMULARIO
#         observaciones = request.POST.get('observaciones', '')
#         total_orden = request.POST.get('total_orden', '0')
#         numero_factura = request.POST.get('numero_factura', '')
#         bodega = request.POST.get('bodega_id')

#         try:
#             total_orden_decimal = Decimal(total_orden)
#         except:
#             total_orden_decimal = Decimal('0.00')

#         # Crear la compra relacionada con la orden
#         compra = Compra.objects.create(
#             orden_compra=orden,
#             observaciones=observaciones,
#             total=total_orden_decimal,
#             bodega_id=bodega if bodega else None,
#             numero_factura=numero_factura
#         )
#         print(f">>> Compra creada con ID: {compra.id}")

#         # Crear los items de la compra copiando los de la orden
#         for item in orden.items.all():
#             ItemCompra.objects.create(
#                 compra=compra,
#                 producto=item.producto,
#                 cantidad_recibida=item.cantidad,
#                 precio_unitario=item.precio_unitario
#             )
#             print(f">>> ItemCompra creado para producto: {item.producto.nombre}")

#         return redirect('list_orden_y_compra')

#     print(">>> GET recibido: mostrando formulario")  # Verifica que entra en GET también
#     return render(request, 'comprarOrden.html', {
#         'orden': orden,
#         'items': orden.items.all()
#     })
    

# @transaction.atomic
# def comprar_orden(request, id):
#     orden = get_object_or_404(OrdenCompra, id=id)

#     if request.method == 'POST':
#         # ✅ Verificar si ya existe una compra asociada
#         if hasattr(orden, 'compra'):
#             messages.error(request, "Esta orden ya tiene una compra registrada.")
#             return redirect('ordenes_compra')

#         # Obtener datos del formulario
#         observaciones = request.POST.get('observaciones', '')
#         numero_factura = request.POST.get('numFActura', '')
#         bodega = request.POST.get('bodega_id')

#         # Calcular el total
#         total_orden_decimal = sum(
#             (item.cantidad * item.precio_unitario for item in orden.items.all()),
#             start=Decimal('0.00')
#         )

#         # Crear la compra
#         compra = Compra.objects.create(
#             orden_compra=orden,
#             observaciones=observaciones,
#             total=total_orden_decimal,
#             bodega_id=bodega if bodega else None,
#             numero_factura=numero_factura
#         )

#         # Crear los ítems de la compra
#         for item in orden.items.all():
#             ItemCompra.objects.create(
#                 compra=compra,
#                 producto=item.producto,
#                 cantidad_recibida=item.cantidad,
#                 precio_unitario=item.precio_unitario
#             )
            
#          # Cambia el estado de la orden a "comprada"
#         orden.estado = 'comprada'+' '+compra.numero_factura
#         orden.save()    

#         messages.success(request, "Compra registrada correctamente.")
#         return redirect('ordenes_compra')

#     return render(request, 'comprarOrden.html', {
#         'orden': orden,
#         'items': orden.items.all()
#     })
    

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

        # 📌 Imprimir datos recibidos como depuración (tipo var_dump)
        print(">>> Datos del formulario:")
        print("Observaciones:", observaciones)
        print("Número de factura:", numero_factura)
        print("Bodega ID:", bodega)
        print("POST completo:", dict(request.POST))  # También puedes usar request.POST.items()
        
        if not proveedor_id:
            messages.error(request, "Debe seleccionar un proveedor.")
            return redirect('comprar_orden', id=id)

        try:
            proveedor = Proveedor.objects.get(id_proveedor=proveedor_id)
        except Proveedor.DoesNotExist:
            messages.error(request, "Proveedor no válido.")
            return redirect('comprar_orden', id=id)




        # Calcular el total
        total_orden_decimal = sum(
            (item.cantidad * item.precio_unitario for item in orden.items.all()),
            start=Decimal('0.00')
        )
        print("Total calculado:", total_orden_decimal)
        
       
        

        # Crear la compra
        compra = Compra.objects.create(
            orden_compra=orden,
            observaciones=observaciones,
            total=total,
            fecha_compra = fecha_compra,
            proveedor=proveedor,
            bodega_id=bodega if bodega else None,
            numero_factura=numero_factura
        )

        # Crear los ítems de la compra
        # for item in orden.items.all():
        #     ItemCompra.objects.create(
        #         compra=compra,
        #         producto=item.producto,
        #         cantidad_recibida=item.cantidad,
        #         precio_unitario=item.precio_unitario
        #     )
        for i in range(len(productos)):
            producto_id = productos[i]
            cantidad = int(cantidades[i])
            precio_unitario = Decimal(precios[i].replace(',', ''))  # limpia el formato si viene con comas

            ItemCompra.objects.create(
                compra=compra,
                producto_id=producto_id,
                cantidad_recibida=cantidad,
                precio_unitario=precio_unitario
            )

        # Cambia el estado de la orden a "comprada"
        orden.estado = 'comprada' + ' ' + compra.numero_factura
        orden.save()

        messages.success(request, "Compra registrada correctamente.")
        return redirect('ordenes_compra')
    
    try:
        compra = orden.compra  # usa el related_name
    except Compra.DoesNotExist:
        compra = None

    items = orden.items.all()  # ajusta según tu modelo real
    
   
    return render(request, 'comprarOrden.html', {
        'orden': orden,
        'compra': compra,
        'items': items,
    })

    # return render(request, 'comprarOrden.html', {
    #     'orden': orden,
    #     'items': orden.items.all()
    # }) 



# @transaction.atomic
# def comprar_orden(request, id):
#     orden = get_object_or_404(OrdenCompra, id=id)

#     if request.method == 'POST':
#         # Verificar si ya existe una compra asociada
#         if hasattr(orden, 'compra'):
#             messages.error(request, "Esta orden ya tiene una compra registrada.")
#             return redirect('ordenes_compra')

#         # Obtener datos del formulario
#         proveedor_id = request.POST.get('proveedor').strip()
#         observaciones = request.POST.get('observaciones', '').strip()
#         numero_factura = request.POST.get('numFActura').strip()
#         bodega = request.POST.get('bodega_id', None)
#         total = request.POST.get('total_orden', '0.00')
#         productos = request.POST.getlist('productos[]')
#         cantidades = request.POST.getlist('cantidades[]')
#         precios = request.POST.getlist('precios[]')

#         # Validar proveedor
#         if not proveedor_id:
#             messages.error(request, "Debe seleccionar un proveedor.")
#             return redirect('comprar_orden', id=id)

#         try:
#             proveedor = Proveedor.objects.get(id_proveedor=proveedor_id)
#         except Proveedor.DoesNotExist:
#             messages.error(request, "Proveedor no válido.")
#             return redirect('comprar_orden', id=id)

#         # Calcular total de los productos de la orden por seguridad
#         total_orden_decimal = sum(
#             (item.cantidad * item.precio_unitario for item in orden.items.all()),
#             start=Decimal('0.00')
#         )

#         # Crear la compra
#         compra = Compra.objects.create(
#             orden_compra=orden,
#             observaciones=observaciones,
#             total=total_orden_decimal,
#             proveedor=proveedor,
#             bodega_id=bodega if bodega else None,
#             numero_factura=numero_factura
#         )

#         # Crear los ítems de la compra
#         for i in range(len(productos)):
#             producto_id = productos[i]
#             cantidad = int(cantidades[i])
#             precio_unitario = Decimal(precios[i].replace(',', '').strip())

#             ItemCompra.objects.create(
#                 compra=compra,
#                 producto_id=producto_id,
#                 cantidad_recibida=cantidad,
#                 precio_unitario=precio_unitario
#             )

#         # Cambiar estado de la orden
#         orden.estado = 'comprada ' + compra.numero_factura
#         orden.save()

#         messages.success(request, "Compra registrada correctamente.")
#         return redirect('ordenes_compra')

#     return render(request, 'comprarOrden.html', {
#         'orden': orden,
#         'items': orden.items.all(),
#         'proveedores': Proveedor.objects.all(),  # Solo si lo necesitas en el template
#     })
   

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