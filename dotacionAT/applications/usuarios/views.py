# from django.shortcuts import render
# from django.contrib.auth import authenticate, login
# from django.shortcuts import render, redirect
# from django.contrib import messages
# # Create your views here.

# # Redirección por rol
# # @login_required
# def dashboard_redirect(request):
#     if request.user.rol == 'admin':
#         return redirect('admin_dashboard')
#     elif request.user.rol == 'gerente':
#         return redirect('gerente_dashboard')
#     elif request.user.rol == 'empleado':
#         return redirect('empleado_dashboard')
#     else:
#         return redirect('login')  # fallback
    
# def redirect_por_rol(user):
#     if user.rol == 'admin':
#         return redirect('admin_dashboard')  # Ajusta con tus rutas
#     elif user.rol == 'gerente':
#         return redirect('gerente_dashboard')
#     elif user.rol == 'empleado':
#         return redirect('empleado_dashboard')
#     return redirect('login')    


# def login_usuario(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']

#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             if user.estado == 'activo':  # verificación extra por tu modelo
#                 login(request, user)
#                 return redirect_por_rol(user)
#             else:
#                 messages.error(request, 'Usuario inactivo.')
#         else:
#             messages.error(request, 'Credenciales incorrectas.')

#     return render(request, 'usuarios/login.html')    