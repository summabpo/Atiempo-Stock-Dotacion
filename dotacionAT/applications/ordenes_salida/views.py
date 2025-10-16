from django.shortcuts import render, redirect, get_object_or_404
from .models import Salida, ItemSalida
from django.urls import reverse
from django.http import JsonResponse
# from .forms import OrdenCompraForm
from applications.productos.models import Producto
from applications.clientes.models import Cliente
from applications.bodegas.models import Bodega
from django.forms import modelformset_factory
from django.contrib import messages
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, IntegrityError
from django.contrib.auth.decorators import login_required
from applications.proveedores.models import Proveedor
from applications.ordenes_compra.models import OrdenCompra, ItemOrdenCompra, DiferenciaTraslado
from django.db.models import Q

# Create your views here.

@login_required(login_url='login_usuario')
def ordenes_salida(request):
    ordenes_salida = Salida.objects.all()
    return render (request, 'ordenesSalida.html', {
        'ordenes_salida': ordenes_salida
    })
    
   
# @login_required(login_url='login_usuario')
# def list_orden_salida(request):
#     # base queryset
#     salidas = Salida.objects.select_related(
#         'bodegaEntrada', 'bodegaSalida', 'cliente', 'usuario_creador__sucursal'
#     )

#     # 🔒 Restricción por rol
#     if request.user.rol == "almacen":
#         salidas = salidas.filter(usuario_creador__sucursal=request.user.sucursal)

#     data = []
#     for salida in salidas:
#         data.append({
#             'id': salida.id,
#             'cliente': salida.cliente.nombre if salida.cliente else "Sin cliente",
#             'fecha': salida.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if salida.fecha_creacion else '',
#             'tipo_documento': salida.tipo_documento,
#             'bodegaSalida': salida.bodegaSalida.nombre if salida.bodegaSalida else "Sin bodega",
#             'bodegaEntrada': salida.bodegaEntrada.nombre if salida.bodegaEntrada else "Sin bodega",
#             'usuario': (
#                 f"{salida.usuario_creador.get_full_name()} - {salida.usuario_creador.sucursal.nombre}"
#                 if salida.usuario_creador and salida.usuario_creador.sucursal else
#                 salida.usuario_creador.get_full_name() if salida.usuario_creador else "Sin usuario"
#             ),
#             'estado_orden_compra': (
#                 salida.orden_compra_asociada.estado 
#                 if salida.orden_compra_asociada else 
#                 "Sin orden asociada"
#             ),
#             'id_orden': salida.orden_compra_asociada.id if salida.orden_compra_asociada else '',
#             'url_editar': f'/detalle_salida/{salida.id}/',
#         })

#     return JsonResponse({'ordenes_salida': data}) 

@login_required(login_url='login_usuario')
def list_orden_salida(request):
    salidas = Salida.objects.select_related(
        'bodegaEntrada', 'bodegaSalida', 'cliente', 'usuario_creador__sucursal'
    )

    if request.user.rol == "almacen":
        salidas = salidas.filter(usuario_creador__sucursal=request.user.sucursal)

    data = []
    for salida in salidas:
        # 🔍 Verificar si tiene diferencias pendientes
        tiene_diferencias = salida.diferencias.filter(resuelto=False).exists()

        data.append({
            'id': salida.id,
            'cliente': salida.cliente.nombre if salida.cliente else "Sin cliente",
            'fecha': salida.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if salida.fecha_creacion else '',
            'tipo_documento': salida.tipo_documento,
            'bodegaSalida': salida.bodegaSalida.nombre if salida.bodegaSalida else "Sin bodega",
            'bodegaEntrada': salida.bodegaEntrada.nombre if salida.bodegaEntrada else "Sin bodega",
            'usuario': (
                f"{salida.usuario_creador.get_full_name()} - {salida.usuario_creador.sucursal.nombre}"
                if salida.usuario_creador and salida.usuario_creador.sucursal else
                salida.usuario_creador.get_full_name() if salida.usuario_creador else "Sin usuario"
            ),
            'estado_orden_compra': (
                salida.orden_compra_asociada.estado 
                if salida.orden_compra_asociada else 
                "Sin orden asociada"
            ),
            'id_orden': salida.orden_compra_asociada.id if salida.orden_compra_asociada else '',
            'url_editar': f'/detalle_salida/{salida.id}/',
            
            # 👇 Nuevo campo para la grid
            'tiene_diferencias': tiene_diferencias,
        })

    return JsonResponse({'ordenes_salida': data}) 


@transaction.atomic
def crear_salida(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('proveedor')
        productos = request.POST.getlist('productosNew[]')
        cantidades = request.POST.getlist('cantidades[]')
        #precios = request.POST.getlist('precios[]')
        # tipo_documento = request.POST.getlist('tipoDoc[]')
        # estado = request.POST.getlist('estado[]')
        precios = 0
        bodegaSalida = request.POST.get('bodegaSalida')
        bodegaEntrada = request.POST.get('bodegaEntrada')
        #total_orden = request.POST.get('total_orden')
        total_orden = 0
        
        print(request.POST)
        

        
        # Validación temprana para cliente y productos
        if not cliente_id or not productos:
            messages.error(request, "Debe seleccionar un cliente y al menos un producto.")
            return redirect('crear_salida')

        # 💰 Conversión segura del total
        # try:
        #     total_orden_decimal = Decimal(total_orden)
        # except:
        #     total_orden_decimal = Decimal('0.00')

        try:
            cliente = Cliente.objects.get(id_cliente=cliente_id)
            bodegaSalida = Bodega.objects.get(id_bodega=bodegaSalida)
            if bodegaEntrada:
                bodegaEntrada = Bodega.objects.get(id_bodega=bodegaEntrada)
            else:
                bodegaEntrada = None
            
            if cliente.nombre.lower() == 'atiempo sas' or cliente.id_cliente == 1:
                tipo_documento = 'TRS'
                estado = 'Pendiente'
            else:
                tipo_documento = 'SI'
                estado = 'salida'    
       
        except Cliente.DoesNotExist:
            messages.error(request, "Cliente no válido.")
            return redirect('crear_salida')

        # Revisa si hay productos válidos
        productos_validos = 0  # Para contar productos con cantidad > 0
        items = []
        
        print(request.POST)

        for i in range(len(productos)):
            try:
                cantidad = int(cantidades[i])
                precio_unitario = 0

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
            messages.error(request, "No se puede agregar la orden porque hay productos con cantidad 0")
            return redirect('crear_salida')

        # Crear la salida principal
        salida = Salida.objects.create(
            tipo_documento = tipo_documento,
            estado = estado, 
            cliente=cliente,  # Si es el proveedor que corresponde a 'cliente', asignalo así
            total= 0,
            bodegaSalida = bodegaSalida,
            bodegaEntrada = bodegaEntrada,
            usuario_creador=request.user
            #observaciones=observaciones,
            # Aquí puedes agregar cualquier otro campo necesario, como tipo_documento, bodega, etc.
        )
        
        # 🔹 Crear los ítems asociados a la salida
        for item in items:
            ItemSalida.objects.create(
                salida=salida,
                producto_id=item['producto_id'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio_unitario']
            )
        
#Comentado
        if tipo_documento == 'TRS' and bodegaEntrada:  
            proveedor_nombre = f"Traslado interno - {bodegaEntrada.nombre}"

            proveedor, _ = Proveedor.objects.get_or_create(
                nombre=proveedor_nombre,
                defaults={
                    "direccion": "Interno",
                    "ciudad": bodegaEntrada.id_ciudad,  # 👈 aquí va el FK correcto
                    "usuario_creador": request.user
                }
            )

            orden = OrdenCompra.objects.create(
                proveedor=proveedor,
                observaciones=f"Traslado desde {bodegaSalida.nombre} hacia {bodegaEntrada.nombre}",
                total=Decimal("0.00"),
                usuario_creador=request.user,
                tipo_documento="TRS"
            )
            
            # 👇 Relacionamos la orden con la salida
            salida.orden_compra_asociada = orden
            salida.save()

            for item in items:
                ItemOrdenCompra.objects.create(
                    orden=orden,
                    producto_id=item['producto_id'],
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio_unitario']
                )

        messages.success(request, "Orden de salida creada correctamente.")
        return redirect('ordenes_salida')

    productos = Producto.objects.all()
    return render(request, 'crear_salida.html', {'productos': productos})



def detalle_salida(request, id):
    detalle_salida = get_object_or_404(Salida, id=id) 
    items = detalle_salida.items.all()
    return render(request, 'ver_salida.html', {
        'detalle_salida': detalle_salida,
        'items': items,
    })
    
    
    
    
    
    
    
    
    
def diferencias_por_salida(request, salida_id):
    diferencias = DiferenciaTraslado.objects.filter(salida__id=salida_id).select_related('producto', 'compra')
    
    data = []
    for d in diferencias:
        data.append({
            'id': d.id,
            'producto': d.producto.nombre,
            'cantidad_enviada': d.cantidad_enviada,
            'cantidad_recibida': d.cantidad_recibida,
            'diferencia': d.diferencia,
            'observacion': d.observacion or '',
            'resuelto': d.resuelto,
            'fecha_registro': d.fecha_registro.strftime('%Y-%m-%d %H:%M'),
            'compra': d.compra.id,
        })
    
    return JsonResponse({'diferencias': data})