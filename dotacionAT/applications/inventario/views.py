from django.shortcuts import render
from .models import InventarioBodega

def inventario_bodega_list(request):
    inventario = InventarioBodega.objects.select_related('bodega', 'producto').all()
    return render(request, 'inventario_list.html', {
        'inventario': inventario
    })

# Create your views here.




