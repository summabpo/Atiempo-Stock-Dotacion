from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from .models import OrdenCompra, ItemOrdenCompra, Compra, ItemCompra
from django.urls import reverse
from django.http import JsonResponse
from .forms import OrdenCompraForm
from applications.productos.models import Producto
from applications.proveedores.models import Proveedor
from django.forms import modelformset_factory
from django.db import transaction
from django.contrib import messages



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
            'estado': orden.estado,
            'url_editar': f'/comprar_orden/{orden.id}/'
        })

    # Añadir compras
    for compra in compras:
        data.append({
            'id': compra.id,
            'proveedor': compra.orden_compra.proveedor.nombre,
            'fecha': compra.fecha_recepcion.strftime('%Y-%m-%d'),
            'tipo_documento': compra.tipo_documento,
            'total': compra.total,
            'estado': 'Compra',
            'url_editar': f'/comprar_orden/{compra.orden_compra.id}/'
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
@transaction.atomic
def crear_orden_compra(request):
    if request.method == 'POST':
        print("Token recibido:", request.POST.get("csrfmiddlewaretoken"))
        proveedor_id = request.POST.get('proveedor')
        observaciones = request.POST.get('observaciones', '')

        if proveedor_id:
            proveedor = Proveedor.objects.get(id_proveedor=proveedor_id)
            orden = OrdenCompra.objects.create(proveedor=proveedor, observaciones=observaciones)

            productos = request.POST.getlist('productos[]')
            cantidades = request.POST.getlist('cantidades[]')
            precios = request.POST.getlist('precios[]')

            for i in range(len(productos)):
                ItemOrdenCompra.objects.create(
                    orden=orden,
                    producto_id=productos[i],
                    cantidad=cantidades[i],
                    precio_unitario=precios[i]
                )
            messages.success(request, "Orden Compra Creada Correctamente. ! ")    
            return redirect('ordenes_compra')  # redirige a donde tengas la lista de órdenes

    productos = Producto.objects.all()
    return render(request, 'crearOrdenCompra.html', {
        'productos': productos
    })
    
def comprar_orden_vista(request):
    comprar_orden = OrdenCompra.objects.all()
    return render (request, 'comprarOrden.html', {
        'comprar_orden': comprar_orden
    })    
    
    
# def comprar_orden(request, id):
#     orden = get_object_or_404(OrdenCompra, id=id)
#     items = orden.items.all()  # gracias al related_name='items' en el modelo

#     return render(request, 'comprarOrden.html', {
#         'orden': orden,
#         'items': items,
#     })
    
    
@transaction.atomic
def comprar_orden(request, id):
    orden = get_object_or_404(OrdenCompra, id=id)

    if request.method == 'POST':
        print(">>> POST recibido: procesando compra")  # Este debe aparecer en tu consola

        # Crear compra relacionada con la orden
        compra = Compra.objects.create(
            orden_compra=orden,
            observaciones=orden.observaciones
        )
        print(f">>> Compra creada con ID: {compra.id}")

        # Crear los items de la compra copiando los de la orden
        for item in orden.items.all():
            ItemCompra.objects.create(
                compra=compra,
                producto=item.producto,
                cantidad_recibida=item.cantidad,
                precio_unitario=item.precio_unitario
            )
            print(f">>> ItemCompra creado para producto: {item.producto.nombre}")

        return redirect('list_orden_y_compra')

    print(">>> GET recibido: mostrando formulario")  # Verifica que entra en GET también
    return render(request, 'comprarOrden.html', {
        'orden': orden,
        'items': orden.items.all()
    })
    

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
    