from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from .models import Salida, ItemSalida
from django.urls import reverse
from django.http import JsonResponse
# from .forms import OrdenCompraForm
from applications.productos.models import Producto
from applications.clientes.models import Cliente
from django.forms import modelformset_factory
from django.contrib import messages
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, IntegrityError

# Create your views here.


def ordenes_salida(request):
    ordenes_salida = Salida.objects.all()
    return render (request, 'ordenesSalida.html', {
        'ordenes_salida': ordenes_salida
    })
    
    
def list_orden_salida(request):
    
    salidas = Salida.objects.select_related('bodega', 'cliente')

    data = []

    # Añadir compras
    for salida in salidas:
        data.append({
            'id': salida.id,
            'cliente': salida.cliente.nombre,
            'fecha': '',
            'tipo_documento': salida.tipo_documento,
            'total': salida.total,
            'url_editar': '',
            # 'url_editar': f'/detalle_salida/{salida.id}/',
        })

    return JsonResponse({'ordenes_salida': data})    



@transaction.atomic
def crear_salida(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('proveedor')
        productos = request.POST.getlist('productosNew[]')
        cantidades = request.POST.getlist('cantidades[]')
        precios = request.POST.getlist('precios[]')
        observaciones = request.POST.get('observacion')
        total_orden = request.POST.get('total_orden')
        
        # print(request.POST)
        
        # print("Productos:", cliente_id)
        # print("Cantidades:", cantidades)
        # print("Precios:", productos)
        # print("Total:", total)

        
        # Validación temprana para cliente y productos
        if not cliente_id or not productos:
            messages.error(request, "Debe seleccionar un cliente y al menos un producto.")
            return redirect('crear_salida')

        # 💰 Conversión segura del total
        try:
            total_orden_decimal = Decimal(total_orden)
        except:
            total_orden_decimal = Decimal('0.00')

        try:
            cliente = Cliente.objects.get(id_cliente=cliente_id)
        except Cliente.DoesNotExist:
            messages.error(request, "Cliente no válido.")
            return redirect('crear_salida')

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
            messages.error(request, "No se puede agregar la orden porque hay productos con cantidad 0")
            return redirect('crear_salida')

        # Crear la salida principal
        salida = Salida.objects.create(
            cliente=cliente,  # Si es el proveedor que corresponde a 'cliente', asignalo así
            total= 0,
            observaciones=observaciones,
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