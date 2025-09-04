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

# Create your views here.

@login_required(login_url='login_usuario')
def ordenes_salida(request):
    ordenes_salida = Salida.objects.all()
    return render (request, 'ordenesSalida.html', {
        'ordenes_salida': ordenes_salida
    })
    
   
@login_required(login_url='login_usuario')    
def list_orden_salida(request):
    
    salidas = Salida.objects.select_related('bodegaEntrada', 'bodegaSalida', 'cliente')

    data = []

    # Añadir compras
    for salida in salidas:
        data.append({
            'id': salida.id,
            'cliente': salida.cliente.nombre,
            'fecha': salida.fecha_creacion,
            'tipo_documento': salida.tipo_documento,
            'bodegaSalida': salida.bodegaSalida.nombre,
            'url_editar': f'/detalle_salida/{salida.id}/',
            # 'url_editar': f'/detalle_salida/{salida.id}/',
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
                tipo_documento = 'TR'
                estado = 'Traslado'
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

        # Ahora crea los ítems vinculados a esa salida
        for item in items:
            ItemSalida.objects.create(
                salida=salida,  # Vinculamos el ItemSalida a la salida recién creada
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