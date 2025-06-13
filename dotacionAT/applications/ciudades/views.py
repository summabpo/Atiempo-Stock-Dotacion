# from django.shortcuts import render
# from .forms import CiudadFormCrear

# # Create your views here.

# def Ciudad(request):
#     ciudad_form = CiudadFormCrear()
#     return render(request, 'ciudad/ciudad.html', {'form':ciudad_form})


from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
# from django.views.generic import CreateView, UpdateView
from django.urls import reverse
from .models import Ciudad
from .forms import CiudadNueva, CiudadActualizaForm
# from django.http import HttpResponseNotAllowed
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required(login_url='login_usuario')
def hello(request, username):
   
    return HttpResponse("<h1>Hola Ciudades %s</h1>" %username)

@login_required(login_url='login_usuario')
def index(request):
    title = 'Ciudades Bodegas'
    return render(request, 'index.html', {
        'title': title
        })  # Si está dentro de 'ciudades' subcarpeta

#def index(request):
#    return HttpResponse('index.html')
@login_required(login_url='login_usuario')
def list_ciudades(_request):
    # ciudades =list(Ciudad.objects.values())
    # data={'ciudades':ciudades}
    # return JsonResponse(data)
    ciudades = Ciudad.objects.all()
    data = {
        'ciudades': [
            {
                'id_ciudad': ciudad.id_ciudad,
                'nombre': ciudad.nombre,
                'activo': ciudad.activo,
                'url_editar': reverse('modificar_ciudad', args=[ciudad.id_ciudad])
            } for ciudad in ciudades
        ]
    }
    return JsonResponse(data)
    
@login_required(login_url='login_usuario')
def ciudades(request):
    #ciudades = list(Ciudad.objects.values())
    ciudades = Ciudad.objects.all().order_by('id_ciudad')
    return render(request, 'ciudades.html', {
        'ciudades': ciudades
    })

@login_required(login_url='login_usuario')
def ciudad(request, id):
    #ciudad = Ciudad.objects.get(id_ciudad=id)
    ciudad = get_object_or_404(Ciudad, id_ciudad=id)
    return HttpResponse('ciudad: %s' % ciudad.nombre)

@login_required(login_url='login_usuario')
def crear_ciudad(request):
    if request.method == 'GET':
        # show interface
        return render(request, 'crear_ciudad.html', {
                      'form': CiudadNueva()
        })
    else:
        Ciudad.objects.create(nombre=request.POST['nombre'])
        messages.success(request, "Ciudad Creada Correctamente. ! ")
        return redirect('ciudades')

# def crear_ciudad(request):
#     #if request.method == 'POST':
#     #     form = CiudadNueva(request.POST)
#     #     if form.is_valid():
#     #         form.save()  # Guarda la nueva ciudad
#     #         return redirect('ciudades.html')  # Redirige a otra página o a la misma página
#     # else:
#     #     form = CiudadNueva()
        
#     data = {
          
#          'form': CiudadNueva() 
#     }  
    
#     return render(request, 'crear_ciudad.html', data)
    
@login_required(login_url='login_usuario')    
def ciudad_detalle(request, id):
    ##ciudad = Ciudad.objects.get(id_ciudad=id)
    ciudad =  get_object_or_404(Ciudad, id_ciudad=id)
    print(ciudad)
    return render(request, 'ciudadDetalle.html',
                  {
                      'ciudad':ciudad
                  })


# Vista para crear una nueva ciudad
# class CiudadCreateView(CreateView):
#     model = Ciudad
#     form_class = CiudadForm
#     template_name = 'ciudad/ciudad_form.html'  # El template que renderiza el formulario
    # success_url = reverse_lazy('ciudad:ciudad-list')  # Redirige a la lista de ciudades

# Vista para editar una ciudad
# class CiudadUpdateView(UpdateView):
#     model = Ciudad
#     form_class = CiudadForm
#     template_name = 'ciudad/ciudad_form.html'  # El mismo template que para crear
    #success_url = reverse_lazy('ciudad:ciudad-list')  # Redirige a la lista de ciudades

# Vista para cambiar el estado de una ciudad a inactivo
# def inactivar_ciudad(request, pk):
#     try:
#         ciudad = Ciudad.objects.get(pk=pk)
#         ciudad.activo = False
#         ciudad.save()
#         return redirect('ciudades:ciudad-list')
#     except Ciudad.DoesNotExist:
#         return HttpResponseNotAllowed("Ciudad no encontrada.")



@login_required(login_url='login_usuario')
def modificar_ciudad(request, id):
    
    ciudad =  get_object_or_404(Ciudad, id_ciudad=id)
    # print(ciudad)
    # return render(request, 'ciudadDetalle.html',
    #               {
    #                   'ciudad':ciudad
    #               })
    
    data = {
        'form': CiudadActualizaForm(instance=ciudad)
    }
    
    
    if request.method == 'POST':
        formulario = CiudadActualizaForm(data=request.POST, instance=ciudad)
        if formulario.is_valid():
            ciudad_actualizada = formulario.save(commit=False)
            ciudad_actualizada.id_usuario_update = request.user  # ← aquí actualizas el campo
            ciudad_actualizada.save()
            messages.success(request, "Ciudad Actualizada Correctamente. ! ")
            return redirect(to='ciudades')
        data['form'] = formulario
            
    return render(request, 'editarCiudad.html', data)