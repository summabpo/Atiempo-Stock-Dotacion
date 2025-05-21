from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Cliente
from django.urls import reverse
from .forms import ClienteForm
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
                 'url_editar': reverse('modificar_cliente', args=[c.id_cliente])
            } for c in cliente
        ]
    }
    return JsonResponse(data)     


def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()  # Guardar el nuevo proveedor
            messages.success(request, "Cliente Actualizada Correctamente. ! ")
            return redirect('cliente')  # Redirigir después de guardar
    else:
        form = ClienteForm()

    return render(request, 'crear_cliente.html', {'form': form})



def modificar_cliente(request, id):
    
    cliente =  get_object_or_404(Cliente, id_cliente=id)
    # print(ciudad)
    # return render(request, 'ciudadDetalle.html',
    #               {
    #                   'ciudad':ciudad
    #               })
    
    data = {
        'form': ClienteForm(instance=cliente)
    }
    
    
    if request.method == 'POST':
        formulario = ClienteForm(data=request.POST, instance=cliente)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Cliente Actualizada Correctamente. ! ")
            return redirect(to='cliente')
        data['form'] = formulario
            
    return render(request, 'editarCliente.html', data)  