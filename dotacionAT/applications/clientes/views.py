from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Cliente
from django.urls import reverse
# from .forms import ProveedorForm
from django.contrib import messages

# Create your views here.



def cliente(request):
    #ciudades = list(Ciudad.objects.values())
    cliente = Cliente.objects.all()
    return render(request, 'clientes.html', {
        'cliente': cliente
    })
    
def list_clientes(_request):
    # def list_Cliente(request):
    # proveedores =list(Proveedor.objects.values())
    # data={'proveedores':proveedores}
    # return JsonResponse(data)
    cliente = Cliente.objects.all()
    data = {
        'cliente': [
            {
                'id_cliente': c.id_cliente,
                'nombre': c.nombre,
                'telefono': c.telefono,
                'email': c.email,
                'direccion': c.direccion,
                'id_ciudad': c.ciudad.nombre,  # <-- corregido
                'activo': c.activo,
                'url_editar': '1'
            } for c in cliente
        ]
    }
    return JsonResponse(data)     