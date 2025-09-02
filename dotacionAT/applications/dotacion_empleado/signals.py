# from .utils import crear_historial_ingreso_inicial
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from .forms import CargarArchivoForm

# @login_required(login_url='login_usuario')
# def crear_empleado(request):
#     if request.method == 'POST':
#         form = CargarArchivoForm(request.POST)
#         if form.is_valid():
#             empleado = form.save()
#             # 👇 Llamada a utils
#             crear_historial_ingreso_inicial(empleado)
#             return redirect('empleados')
#     else:
#         form = CargarArchivoForm()
#     return render(request, 'crear_empleado.html', {'form': form})