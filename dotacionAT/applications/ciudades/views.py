# from django.shortcuts import render
# from .forms import CiudadFormCrear

# # Create your views here.

# def Ciudad(request):
#     ciudad_form = CiudadFormCrear()
#     return render(request, 'ciudad/ciudad.html', {'form':ciudad_form})


from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
# from django.views.generic import CreateView, UpdateView
# from django.urls import reverse_lazy
from .models import Ciudad
from .forms import CiudadNueva
# from django.http import HttpResponseNotAllowed


def hello(request, username):
   
    return HttpResponse("<h1>Hola Ciudades %s</h1>" %username)


def index(request):
    title = 'Ciudades Bodegas'
    return render(request, 'index.html', {
        'title': title
        })  # Si está dentro de 'ciudades' subcarpeta

#def index(request):
#    return HttpResponse('index.html')

def ciudades(request):
    #ciudades = list(Ciudad.objects.values())
    ciudades = Ciudad.objects.all()
    return render(request, 'ciudades.html', {
        'ciudades': ciudades
    })

def ciudad(request, id):
    #ciudad = Ciudad.objects.get(id_ciudad=id)
    ciudad = get_object_or_404(Ciudad, id_ciudad=id)
    return HttpResponse('ciudad: %s' % ciudad.nombre)

def crear_ciudad(request):
    if request.method == 'GET':
        # show interface
        return render(request, 'crear_ciudad.html', {
                      'form': CiudadNueva()
        })
    else:
        Ciudad.objects.create(nombre=request.POST['nombre'])
        return redirect('ciudades')
    
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
