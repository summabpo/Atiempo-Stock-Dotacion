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

    if request.user.rol == "almacen":
        # Solo usuarios con rol "almacen" → inventario de su propia sucursal
        inventarios = InventarioBodega.objects.select_related("bodega", "producto").filter(
            bodega=request.user.sucursal
        )
    else:
        # Cualquier otro rol → puede ver todas las bodegas
        inventarios = InventarioBodega.objects.select_related("bodega", "producto")

    # Si además mandan un parámetro GET para filtrar por bodega
    if bodega_id:
        inventarios = inventarios.filter(bodega_id=bodega_id)

    data = {
        'inventarios': [
            {
                'id': inv.id,
                'bodega': inv.bodega.nombre,
                'bodega_id': inv.bodega.id_bodega,
                'producto': inv.producto.nombre,
                'id_producto': inv.producto.id_producto,
                'entradas': inv.entradas,
                'salidas': inv.salidas,
                'stock': inv.stock,
                'ultima_entrada': inv.ultima_entrada,
                'ultima_salida': inv.ultima_salida
            }
            for inv in inventarios
        ]
    }
    return JsonResponse(data)


#comento este codigo era el que estaba antes del que dejo arriba este esta sin filtros por rol

# @login_required(login_url='login_usuario')
# def inventario_bodega_json(request):
#     bodega_id = request.GET.get('bodega')
#     inventarios = InventarioBodega.objects.all()

#     if bodega_id:
#         inventarios = inventarios.filter(bodega_id=bodega_id)

#     data = {
#         'inventarios': [
#             {
#                 'id': inventario.id,
#                 'bodega': inventario.bodega.nombre,
#                 'bodega_id': inventario.bodega.id_bodega,
#                 'producto': inventario.producto.nombre,  # <-- corregido
#                 'id_producto': inventario.producto.id_producto,  # <-- corregido
#                 'entradas': inventario.entradas,
#                 'salidas': inventario.salidas,
#                 'stock': inventario.stock,
#                 'ultima_entrada': inventario.ultima_entrada,
#                 'ultima_salida': inventario.ultima_salida
#             } for inventario in inventarios
#         ]
#     }

#     return JsonResponse(data)

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


@login_required
def index(request):
    user = request.user

    # --- Si es rol "almacen", filtrar solo su bodega ---
    if user.rol == "almacen":  
        if user.sucursal:  # 👈 ahora sí
            todos = InventarioBodega.objects.filter(bodega=user.sucursal)
            productos_bajos = (
                InventarioBodega.objects
                .filter(bodega=user.sucursal, stock__lt=8)
                .order_by("stock")[:15]
            )
            print(f"👷 Usuario Almacén -> filtrando por bodega: {user.sucursal.nombre}")
        else:
            todos = InventarioBodega.objects.none()
            productos_bajos = InventarioBodega.objects.none()
            print(f"⚠️ Usuario {user.username} es rol Almacén pero no tiene bodega asignada")
    else:
        # --- Usuarios con otro rol (ej. admin) ven todo ---
        todos = InventarioBodega.objects.all()
        productos_bajos = (
            InventarioBodega.objects
            .filter(stock__lt=8)
            .order_by("stock")[:15]
        )
        print(f"👑 Usuario {user.username} -> ve todos los inventarios")

    return render(request, "index.html", {
        "productos_bajos": productos_bajos
    })