from django.shortcuts import render
from .models import InventarioBodega
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
# Create your views here.

def inventario_bodega_list(request):
    inventario = InventarioBodega.objects.select_related('bodega', 'producto').all()
    return render(request, 'inventario.html', {
        'inventario': inventario

    })


def inventario_bodega_json(_request):
    inventarios = InventarioBodega.objects.all()
    
    data = {
        'inventarios': [
            {
                'id': inventario.id,
                'bodega': inventario.bodega.nombre,
                'producto': inventario.producto.nombre,  # <-- corregido
                'entradas': inventario.entradas,
                'salidas': inventario.salidas,
                'stock': inventario.stock,
                'ultima_entrada': inventario.ultima_entrada,
                'ultima_salida': inventario.ultima_salida
            } for inventario in inventarios
        ]
    }

    return JsonResponse(data)

