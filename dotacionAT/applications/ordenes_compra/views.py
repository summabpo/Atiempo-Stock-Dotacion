from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from .models import OrdenCompra, ItemOrdenCompra
from django.urls import reverse
from django.http import JsonResponse
from .forms import OrdenCompraForm
from applications.productos.models import Producto
from applications.proveedores.models import Proveedor

# Create your views here.

def list_orden_compra(_request):
    # orden_compra =list(OrdenCompra.objects.values())
    # data={'orden_compra':orden_compra}
    # return JsonResponse(data)
    orden_compras = OrdenCompra.objects.all()
    data = {
        'orden_compra': [
            {
                'id': orden_compra.id,
                'proveedor': orden_compra.proveedor.nombre,
                'estado': orden_compra.estado,                
                'fecha': orden_compra.fecha_creacion,
                'observacion': orden_compra.observaciones,
                # 'url_editar': reverse(args=[orden_compra.id])
            } for orden_compra in orden_compras
        ]
    }
    return JsonResponse(data)


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

            return redirect('ordenes_compra')  # redirige a donde tengas la lista de órdenes

    productos = Producto.objects.all()
    return render(request, 'crearOrdenCompra.html', {
        'productos': productos
    })