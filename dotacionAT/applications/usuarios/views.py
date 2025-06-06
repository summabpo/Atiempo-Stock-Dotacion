from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
# Create your views here.

# Redirección por rol


# Vista para redireccionar por rol
@login_required
def dashboard_redirect(request):
    return redirect(redirect_por_rol(request.user))


# Retorna el nombre de la URL según el rol del usuario
def redirect_por_rol(user):
    if user.rol == 'admin':
        return 'admin_dashboard'  # Asegúrate de tener esta ruta definida
    elif user.rol == 'gerente':
        return 'gerente_dashboard'
    elif user.rol == 'empleado':
        return 'empleado_dashboard'
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
                return redirect(redirect_por_rol(user))
            else:
                messages.error(request, 'Usuario inactivo.')
        else:
            messages.error(request, 'Credenciales incorrectas.')

    return render(request, 'login.html')  # Asegúrate de tener este template