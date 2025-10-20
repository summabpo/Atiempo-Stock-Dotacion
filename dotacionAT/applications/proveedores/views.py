from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Proveedor
from django.urls import reverse
from .forms import ProveedorForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import unicodedata
from django.utils.html import escape

def normalizar_nombre_proveedor(nombre):
    nombre = unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('utf-8')
    nombre = nombre.lower().strip().replace(" ", "")
    return nombre


@login_required(login_url='login_usuario')
def proveedor(request):
    #ciudades = list(Ciudad.objects.values())
    proveedor = Proveedor.objects.all()
    return render(request, 'proveedores.html', {
        'proveedores': proveedor
    })

@login_required(login_url='login_usuario')
def list_proveedores(request):
    proveedores =list(Proveedor.objects.values())
    data={'proveedores':proveedores}
    return JsonResponse(data)
def list_proveedores(_request):

    proveedores = Proveedor.objects.all()
    data = {
        'proveedores': [
            {
                'id_proveedor': p.id_proveedor,
                'nombre': p.nombre,
                'telefono': p.telefono,
                'email': p.email,
                'direccion': p.direccion,
                'id_ciudad': p.ciudad.nombre,  # <-- corregido
                'activo': p.activo,
                'url_editar': reverse('modificar_proveedor', args=[p.id_proveedor])
            } for p in proveedores
        ]
    }
    return JsonResponse(data) 
    
@login_required(login_url='login_usuario')    
def crear_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            nombre_ingresado = form.cleaned_data['nombre']
            nombre_normalizado = normalizar_nombre_proveedor(nombre_ingresado)

            for p in Proveedor.objects.all():
                if normalizar_nombre_proveedor(p.nombre) == nombre_normalizado:
                    messages.error(
                        request,
                        f"⚠️ El proveedor {escape(nombre_ingresado)} ya está registrado como {p.nombre}."
                    )
                    return render(request, 'crear_proveedor.html', {'form': form})

            proveedor = form.save(commit=False)
            proveedor.usuario_creador = request.user
            proveedor.save()
            messages.success(request, "Proveedor creado correctamente. ¡")
            return redirect('proveedores')
    else:
        form = ProveedorForm()

    return render(request, 'crear_proveedor.html', {'form': form})


@login_required(login_url='login_usuario')
def proveedor_detalle(request, id):
    
    proveedor =  get_object_or_404(Proveedor, id_proveedor=id)
    print(proveedor)
    return render(request, 'proveedorDetalle.html',
                  {
                      'proveedor':proveedor
                  })    
    
    
@login_required(login_url='login_usuario')
def modificar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id_proveedor=id)
    
    data = {
        'form': ProveedorForm(instance=proveedor)
    }

    if request.method == 'POST':
        formulario = ProveedorForm(data=request.POST, instance=proveedor)
        if formulario.is_valid():
            proveedor = formulario.save(commit=False)
            proveedor.usuario_editor = request.user
            proveedor.save()
            messages.success(request, "Proveedor Actualizado Correctamente. ! ")
            return redirect(to='proveedores')
        data['form'] = formulario

    return render(request, 'editarProveedor.html', data) 