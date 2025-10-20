from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Usuario
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from .forms import UsuarioForm  # Asegúrate de importar el formulario
# Create your views here.

# Vista para redireccionar por rol
@login_required
def dashboard_redirect(request):
    return redirect(redirect_por_rol(request.user))

# Retorna el nombre de la URL según el rol del usuario
def redirect_por_rol(user):
    if user.rol == 'admin':
        return 'index'  # Asegúrate de tener esta ruta definida
    elif user.rol == 'gerente':
        return 'index'
    elif user.rol == 'contable':
        return 'index'
    elif user.rol == 'empleado':
        return 'index'
    elif user.rol == 'almacen':
        return 'index'
    return 'login'  # fallback por si no tiene rol

# Vista de login
def login_usuario(request):
    if request.user.is_authenticated:
        # Si ya está autenticado, redirige según su rol
        return redirect(redirect_por_rol(request.user))

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.estado == 'activo':  # Validación personalizada de tu modelo
                login(request, user)

                # 🔍 Imprimir datos del usuario en consola
                print("=== Usuario autenticado ===")
                print(f"ID: {user.id}")
                print(f"Username: {user.username}")
                print(f"Nombre completo: {user.get_full_name()}")
                print(f"Rol: {user.rol}")
                print(f"Estado: {user.estado}")
                print(f"sucursal: {user.sucursal}")
                print(f"Es activo (Django): {user.is_active}")
                print("===========================")

                return redirect(redirect_por_rol(user))
            else:
                messages.error(request, 'Usuario inactivo.')
        else:
            messages.error(request, 'Credenciales incorrectas.')

    return render(request, 'login.html')  # Asegúrate de tener este template

@login_required(login_url='login_usuario')
def usuario(request):
    #ciudades = list(Ciudad.objects.values())
    usuario = Usuario.objects.all()
    return render(request, 'usuarios.html', {
        'usuario': usuario
    })
    
    
@login_required(login_url='login_usuario')    
def list_usuarios(_request):

    usuario = Usuario.objects.all()
    data = {
        'usuario': [
            {
                'id': c.id,
                'nombre': c.username,
                'email': c.email,
                'rol': c.rol,
                'estado': 'activo' if c.estado == 'activo' else 'inactivo',  # ✅ CORREGIDO
                'estado_display': 'Activo' if c.estado == 'activo' else 'Inactivo',  # ✅ AGREGADO
                'fecha_creacion': c.fecha_creacion
                # 'url_editar': reverse('modificar_cliente', args=[c.id])
            } for c in usuario
        ]
    }
    return JsonResponse(data) 


@login_required(login_url='login_usuario')
def crear_usuario(request):
    if request.method == "POST":
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Usuario creado correctamente.")
            return redirect("usuario")  # Ajusta a tu url real de listado
        else:
            messages.error(request, "❌ Error al crear el usuario. Revisa el formulario.")
    else:
        form = UsuarioForm()

    return render(request, "crear_usuario.html", {"form": form})


def editar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Usuario '{usuario.username}' actualizado correctamente.")
            return redirect('usuario')  # o donde quieras volver
        else:
            messages.error(request, "❌ Corrige los errores antes de continuar.")
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, "editar_usuario.html", {"form": form, "usuario": usuario})