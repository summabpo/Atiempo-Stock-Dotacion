from django.shortcuts import render
from .models import InventarioBodega
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models import F
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

# def index(request):
#     productos_bajos = (
#         InventarioBodega.objects
#         .select_related("producto", "bodega")
#         .order_by("stock")[:15]
#     )
    
#     print("DEBUG → productos bajos:", productos_bajos)  # 👈 revisa la consola

#     return render(request, "index.html", {
#         "productos_bajos": productos_bajos,
#     })


def index(request):
    # Traer TODOS los inventarios para verificar
    todos = InventarioBodega.objects.all()
  
    # Solo los que tienen menos de 8
    productos_bajos = (
        InventarioBodega.objects
        .filter(stock__lt=8)
        .order_by("stock")[:15]
    )

    return render(request, "index.html", {
        "productos_bajos": productos_bajos
    })