
from .models import InventarioBodega
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models import F
from django.utils import timezone
from applications.ordenes_compra.models import Compra, ItemCompra
from .models import InventarioBodega
from applications.productos.models import Producto
from applications.bodegas.models import Bodega

# Create your views here.

@login_required(login_url='login_usuario')
def inventario_bodega_list(request):
    inventario = InventarioBodega.objects.select_related('bodega', 'producto').all()
    return render(request, 'inventario.html', {
        'inventario': inventario

    })


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

    
@login_required(login_url='login_usuario')
def cargar_inventario(request):
    user = request.user  # usuario logueado
    
    if user.rol in ["almacen", "empleado"]:
        # Filtra órdenes de usuarios que pertenezcan a la misma sucursal
        cargar_inventario = InventarioBodega.objects.filter(
            usuario_creador__sucursal=user.sucursal
        )
    else:
        # Admin (o cualquier otro rol) ve todas
        cargar_inventario = InventarioBodega.objects.all()
    
    return render(request, 'cargar_inventario.html', {
        'cargar_inventario': cargar_inventario
    })
    
@login_required(login_url='login_usuario')
def registrar_inventario_inicial(request):
    if request.method == "POST":
        print("Entrando al método POST")
        bodega_id = request.POST.get("bodega")
        productos = request.POST.getlist("productos[]")
        cantidades = request.POST.getlist("cantidades[]")
        observaciones = request.POST.get("observaciones", "")

        bodega = get_object_or_404(Bodega, id_bodega=bodega_id)

        compra = Compra.objects.create(
            bodega=bodega,
            proveedor=None,
            tipo_documento="INVENTARIO_INICIAL",
            usuario_creador=request.user,
            observaciones=observaciones,
            estado="Inventario inicial"
        )

        for i, producto_id in enumerate(productos):
            producto = get_object_or_404(Producto, id_producto=producto_id)
            cantidad = int(cantidades[i])

            ItemCompra.objects.create(
                compra=compra,
                producto=producto,
                cantidad_recibida=cantidad,
                precio_unitario=0
            )
            
            # inventario, creado = InventarioBodega.objects.get_or_create(
            #     bodega=bodega,
            #     producto=producto
            # )
            # inventario.registrar_entrada(cantidad)
            # inventario.usuario_ultima_entrada = request.user
            # inventario.save()
            
        return JsonResponse({"success": True, "message": "Inventario inicial registrado correctamente"})

    else:
        # if request.user.rol in ["admin", "contable"]:
        bodegas = Bodega.objects.all()
        # else:
        #     bodegas = [request.user.sucursal]
        return render(request, "cargar_inventario.html", {"bodegas": bodegas})
        # return render(request, "inventario/cargar_inventario.html", context)