from django.shortcuts import render
from .models import InventarioBodega
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required(login_url='login_usuario')
def inventario_bodega_list(request):
    inventario = InventarioBodega.objects.select_related('bodega', 'producto').all()
    return render(request, 'inventario.html', {
        'inventario': inventario

    })


# def inventario_bodega_json(_request):
#     inventarios = InventarioBodega.objects.all()
    
#     data = {
#         'inventarios': [
#             {
#                 'id': inventario.id,
#                 'bodega': inventario.bodega.nombre,
#                 'bodega_id': inventario.bodega.id_bodega,
#                 'producto': inventario.producto.nombre,  # <-- corregido
#                 'entradas': inventario.entradas,
#                 'salidas': inventario.salidas,
#                 'stock': inventario.stock,
#                 'ultima_entrada': inventario.ultima_entrada,
#                 'ultima_salida': inventario.ultima_salida
#             } for inventario in inventarios
#         ]
#     }

#     return JsonResponse(data)

@login_required(login_url='login_usuario')
def inventario_bodega_json(request):
    bodega_id = request.GET.get('bodega')
    inventarios = InventarioBodega.objects.all()

    if bodega_id:
        inventarios = inventarios.filter(bodega_id=bodega_id)

    data = {
        'inventarios': [
            {
                'id': inventario.id,
                'bodega': inventario.bodega.nombre,
                'bodega_id': inventario.bodega.id_bodega,
                'producto': inventario.producto.nombre,  # <-- corregido
                'id_producto': inventario.producto.id_producto,  # <-- corregido
                'entradas': inventario.entradas,
                'salidas': inventario.salidas,
                'stock': inventario.stock,
                'ultima_entrada': inventario.ultima_entrada,
                'ultima_salida': inventario.ultima_salida
            } for inventario in inventarios
        ]
    }

    return JsonResponse(data)

