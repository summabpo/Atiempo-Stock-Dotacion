from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Cliente
from django.urls import reverse
from .forms import ClienteForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import unicodedata
from django.utils.html import escape

# Create your views here.

def normalizar_nombre(nombre):
    nombre = unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('utf-8')
    nombre = nombre.lower().strip().replace(" ", "")
    return nombre

@login_required(login_url='login_usuario')
def cliente(request):
    #ciudades = list(Ciudad.objects.values())
    cliente = Cliente.objects.all()
    return render(request, 'clientes.html', {
        'cliente': cliente
    })
  
@login_required(login_url='login_usuario')    
def list_clientes(_request):
  
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

@login_required(login_url='login_usuario')
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            nombre_ingresado = form.cleaned_data['nombre']
            nombre_normalizado = normalizar_nombre(nombre_ingresado)

            for c in Cliente.objects.all():
                if normalizar_nombre(c.nombre) == nombre_normalizado:
                    messages.error(
                        request,
                        f"⚠️ El cliente {escape(nombre_ingresado)} ya está registrado como {c.nombre}."
                    )
                    return render(request, 'crear_cliente.html', {'form': form})

            cliente = form.save(commit=False)
            cliente.usuario_creador = request.user
            cliente.save()
            messages.success(request, "Cliente Creado Correctamente. ¡")
            return redirect('cliente')
    else:
        form = ClienteForm()

    return render(request, 'crear_cliente.html', {'form': form})


@login_required(login_url='login_usuario')
def modificar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id_cliente=id)

    data = {
        'form': ClienteForm(instance=cliente)
    }

    if request.method == 'POST':
        formulario = ClienteForm(data=request.POST, instance=cliente)
        if formulario.is_valid():
            cliente = formulario.save(commit=False)
            cliente.usuario_editor = request.user  # 👤 Asignar usuario que edita
            cliente.save()
            messages.success(request, "Cliente Actualizado Correctamente. ! ")
            return redirect(to='cliente')
        data['form'] = formulario  # 👈 Si no es válido, mostrar los errores

    return render(request, 'editarCliente.html', data)  