from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Bodega
from django.urls import reverse
from .forms import BodegaNueva
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required(login_url='login_usuario')
def hello(request):
    return HttpResponse("Hola, bienvenido a Bodegas!")


@login_required(login_url='login_usuario')
def bodegas(request):
    #Bodegaes = list(Bodega.objects.values())
    bodega = Bodega.objects.all()
    return render(request, 'bodegas.html', {
        'bodegas': bodega
    })

@login_required(login_url='login_usuario')    
def list_bodegas(_request):
    # bodegas =list(Bodega.objects.values())
    # data={'bodegas':bodegas}
    # return JsonResponse(data)
    bodegas = Bodega.objects.select_related('id_ciudad')  # ¡importante para eficiencia!
    data = {
        'bodegas': [
            {
                'id_bodega': bodega.id_bodega,
                'nombre': bodega.nombre,
                'ciudad': bodega.id_ciudad.nombre,  # <--- Aquí llega el nombre
                'direccion': bodega.direccion,
                'activo': bodega.estado,
                'url_editar': reverse('modificar_bodega', args=[bodega.id_bodega])
            }
            for bodega in bodegas
        ]
    }
    return JsonResponse(data)    



@login_required(login_url='login_usuario')
# def crear_bodega(request):
#     if request.method == 'POST':
#         form = BodegaNueva(request.POST)
#         if form.is_valid():
#             nueva_bodega = form.save(commit=False)
#             nueva_bodega.id_usuario_creador = request.user  # ← asigna el usuario que crea
#             nueva_bodega.save()
#             messages.success(request, "Bodega Creada Correctamente. ! ")
#             return redirect('bodegas')
#         else:
#             print(form.errors)
#     else:
#         form = BodegaNueva()

#     return render(request, 'crear_bodega.html', {'form': form})
def crear_bodega(request):
    if request.method == 'POST':
        form = BodegaNueva(request.POST)
        if form.is_valid():
            nueva_bodega = form.save(commit=False)
            nombre = nueva_bodega.nombre
            ciudad = nueva_bodega.id_ciudad

            # Verificar si ya existe una bodega con ese nombre en la misma ciudad
            if Bodega.objects.filter(nombre__iexact=nombre, id_ciudad=ciudad).exists():
                messages.warning(request, "⚠️ Ya existe una bodega con ese nombre en esa ciudad.")
                return render(request, 'crear_bodega.html', {'form': form})

            nueva_bodega.id_usuario_creador = request.user
            nueva_bodega.save()
            messages.success(request, "✅ Bodega creada correctamente.")
            return redirect('bodegas')
        else:
            print(form.errors)
    else:
        form = BodegaNueva()

    return render(request, 'crear_bodega.html', {'form': form})


@login_required(login_url='login_usuario')
def bodegas(request):
    #ciudades = list(Ciudad.objects.values())
    bodegas = Bodega.objects.all()
    return render(request, 'bodegas.html', {
        'bodegas': bodegas
    })
    
    
@login_required(login_url='login_usuario')    
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

@login_required(login_url='login_usuario')
def modificar_bodega(request, id):
    bodega = get_object_or_404(Bodega, id_bodega=id)
    data = {
        'form': BodegaNueva(instance=bodega)
    }

    if request.method == 'POST':
        formulario = BodegaNueva(data=request.POST, instance=bodega)
        if formulario.is_valid():
            bodega_actualizada = formulario.save(commit=False)
            bodega_actualizada.id_usuario_editor = request.user  # ← asigna el usuario que edita
            bodega_actualizada.save()
            messages.success(request, "Bodega Actualizada Correctamente. ! ")
            return redirect('bodegas')
        data['form'] = formulario

    return render(request, 'editarBodega.html', data)