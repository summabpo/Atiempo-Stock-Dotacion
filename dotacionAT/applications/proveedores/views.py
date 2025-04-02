from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Proveedor
from .forms import ProveedorForm
from django.contrib import messages

def proveedor(request):
    #ciudades = list(Ciudad.objects.values())
    proveedor = Proveedor.objects.all()
    return render(request, 'proveedores.html', {
        'proveedores': proveedor
    })
    
    
def crear_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()  # Guardar el nuevo proveedor
            messages.success(request, "Proveedor Actualizada Correctamente. ! ")
            return redirect('proveedores')  # Redirigir después de guardar
    else:
        form = ProveedorForm()

    return render(request, 'crear_proveedor.html', {'form': form})


def proveedor_detalle(request, id):
    ##ciudad = Ciudad.objects.get(id_ciudad=id)
    proveedor =  get_object_or_404(Proveedor, id_proveedor=id)
    print(proveedor)
    return render(request, 'proveedorDetalle.html',
                  {
                      'proveedor':proveedor
                  })    
    
    

def modificar_proveedor(request, id):
    
    proveedor =  get_object_or_404(Proveedor, id_proveedor=id)
    # print(ciudad)
    # return render(request, 'ciudadDetalle.html',
    #               {
    #                   'ciudad':ciudad
    #               })
    
    data = {
        'form': ProveedorForm(instance=proveedor)
    }
    
    
    if request.method == 'POST':
        formulario = ProveedorForm(data=request.POST, instance=proveedor)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Proveedor Actualizada Correctamente. ! ")
            return redirect(to='proveedores')
        data['form'] = formulario
            
    return render(request, 'editarProveedor.html', data)  