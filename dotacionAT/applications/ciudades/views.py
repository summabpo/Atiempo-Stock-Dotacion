from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
# from django.views.generic import CreateView, UpdateView
from django.urls import reverse
from .models import Ciudad
from .forms import CiudadNueva, CiudadActualizaForm
# from django.http import HttpResponseNotAllowed
from django.contrib import messages
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe


@login_required(login_url='login_usuario')
def hello(request, username):
   
    return HttpResponse("<h1>Hola Ciudades %s</h1>" %username)

@login_required(login_url='login_usuario')
def index(request):
    title = 'Ciudades Bodegas'
    return render(request, 'index.html', {
        'title': title
        })  # Si está dentro de 'ciudades' subcarpeta


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


ABREVIATURAS_CIUDADES = {
    'apartado': 'Apartadó',
    'apartadó': 'Apartadó',
    'armenia': 'Armenia',
    'baq': 'Barranquilla',
    'barranquilla': 'Barranquilla',
    'bello': 'Bello',
    'bga': 'Bucaramanga',
    'bog': 'Bogotá',
    'bogota': 'Bogotá',
    'bogotá': 'Bogotá',
    'bquilla': 'Barranquilla',
    'bta': 'Bogotá',
    'buca': 'Bucaramanga',
    'bucaramanga': 'Bucaramanga',
    'cali': 'Cali',
    'cartagena': 'Cartagena',
    'cl': 'Cali',
    'ctg': 'Cartagena',
    'ctgena': 'Cartagena',
    'cuc': 'Cúcuta',
    'cucuta': 'Cúcuta',
    'cúcuta': 'Cúcuta',
    'envigado': 'Envigado',
    'florencia': 'Florencia',
    'funza': 'Funza',
    'ibague': 'Ibagué',
    'ibagué': 'Ibagué',
    'ibg': 'Ibagué',
    'itagui': 'Itagüí',
    'itagüí': 'Itagüí',
    'manizales': 'Manizales',
    'manz': 'Manizales',
    'med': 'Medellín',
    'medellin': 'Medellín',
    'medellín': 'Medellín',
    'monteria': 'Montería',
    'montería': 'Montería',
    'mosquera': 'Mosquera',
    'neiva': 'Neiva',
    'pasto': 'Pasto',
    'per': 'Pereira',
    'pereira': 'Pereira',
    'popayan': 'Popayán',
    'popayán': 'Popayán',
    'quibdo': 'Quibdó',
    'quibdó': 'Quibdó',
    'rio hacha': 'Riohacha',
    'riohacha': 'Riohacha',
    'santamarta': 'Santa Marta',
    'santiago': 'Cali',
    'santiagodecali': 'Cali',
    'sincelejo': 'Sincelejo',
    'smr': 'Santa Marta',
    'soacha': 'Soacha',
    'sta marta': 'Santa Marta',
    'tunja': 'Tunja',
    'turbo': 'Turbo',
    'valledupar': 'Valledupar',
    'vcio': 'Villavicencio',
    'villavicencio': 'Villavicencio',
    'vll': 'Villavicencio',
    'vpar': 'Valledupar',
    'yopal': 'Yopal'
}

# Función que convierte abreviaturas en nombres estandarizados
def normalizar_ciudad(nombre):
    clave = slugify(nombre).replace('-', '')  # Ej: "bta" o "Bogota" → "bta" o "bogota"
    return ABREVIATURAS_CIUDADES.get(clave, nombre.title().strip())  # Si no está en el dict, aplica .title()

# Vista para crear ciudad sin duplicados ni abreviaturas confusas
@login_required(login_url='login_usuario')
def crear_ciudad(request):
    if request.method == 'GET':
        return render(request, 'crear_ciudad.html', {'form': CiudadNueva()})
    
    nombre_input = request.POST.get('nombre', '')
    nombre_normalizado = normalizar_ciudad(nombre_input)

    # Verificar si ya existe una ciudad con ese nombre
    if Ciudad.objects.filter(nombre__iexact=nombre_normalizado).exists():
       messages.error(request, f'⚠️ La ciudad {nombre_normalizado} ya está registrada.')
    else:
        Ciudad.objects.create(nombre=nombre_normalizado)
        messages.success(request, f"✅ Ciudad {nombre_normalizado} creada correctamente.")

    return redirect('ciudades')

    
@login_required(login_url='login_usuario')    
def ciudad_detalle(request, id):
    ##ciudad = Ciudad.objects.get(id_ciudad=id)
    ciudad =  get_object_or_404(Ciudad, id_ciudad=id)
    print(ciudad)
    return render(request, 'ciudadDetalle.html',
                  {
                      'ciudad':ciudad
                  })



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