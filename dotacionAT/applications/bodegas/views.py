from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Bodega
from .forms import BodegaNueva
from django.contrib import messages


def hello(request):
    return HttpResponse("Hola, bienvenido a Bodegas!")

def bodegas(request):
    #Bodegaes = list(Bodega.objects.values())
    bodega = Bodega.objects.all()
    return render(request, 'bodegas.html', {
        'bodegas': bodega
    })

def crear_bodega(request):
    if request.method == 'POST':
        # Crear la bodega usando el formulario
        form = BodegaNueva(request.POST)
        if form.is_valid():
            form.save()  # Esto guarda la nueva bodega, incluyendo todos los campos, como id_Bodega
            messages.success(request, "Bodega Actualizada Correctamente. ! ")
            return redirect('bodegas')  # Redirige a la lista de bodegas
        else:
            print(form.errors)  # Imprime los errores del formulario en la consola para depurar
    else:
        form = BodegaNueva()

    return render(request, 'crear_bodega.html', {'form': form})

def bodegas(request):
    #ciudades = list(Ciudad.objects.values())
    bodegas = Bodega.objects.all()
    return render(request, 'bodegas.html', {
        'bodegas': bodegas
    })
    
def bodega_detalle(request, id):
    ##ciudad = Ciudad.objects.get(id_ciudad=id)
    bodega =  get_object_or_404(Bodega, id_bodega=id)
    print(bodega)
    return render(request, 'bodegaDetalle.html',
                  {
                      'bodega':bodega
                  })
    
# def crear_bodega(request):
#     if request.method == 'GET':
#         # show interface
#         return render(request, 'crear_bodega.html', {
#                       'form': BodegaNueva()
#         })
#     else:
#         print("Datos recibidos en el POST:"),
#         print("Nombre de la bodega:", request.POST.get('nombre')),  # Verifica el valor enviado
#         Bodega.objects.create(nombre=request.POST['nombre'])
#         return redirect('bodegas')    
    
# def crear_bodega(request):
#     if request.method == 'POST':
#         print("POST Data:", request.POST)  # Esto imprime los datos enviados en el POST
#         form = BodegaNueva(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('bodegas:lista_bodegas')
#     else:
#         form = BodegaNueva()

#     return render(request, 'bodegas/crear_bodega.html', {'form': form})    


def modificar_bodega(request, id):
    
    bodega =  get_object_or_404(Bodega, id_bodega=id)
    # print(ciudad)
    # return render(request, 'ciudadDetalle.html',
    #               {
    #                   'ciudad':ciudad
    #               })
    
    data = {
        'form': BodegaNueva(instance=bodega)
    }
    

    if request.method == 'POST':
        formulario = BodegaNueva(data=request.POST, instance=bodega)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Bodega Actualizada Correctamente. ! ")
            return redirect(to='bodegas')
        data['form'] = formulario
            
    return render(request, 'editarbodega.html', data)