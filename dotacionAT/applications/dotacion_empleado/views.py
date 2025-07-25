
# import pandas as pd
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from .forms import CargarArchivoForm
# from .models import EmpleadoDotacion
# # Create your views here.


# def cargar_empleados_desde_excel(request):
#     if request.method == 'POST':
#         form = CargarArchivoForm(request.POST, request.FILES)
#         if form.is_valid():
#             archivo = request.FILES['archivo']

#             try:
#                 df = pd.read_excel(archivo)  # También puedes usar read_csv() si es .txt
#                 for _, fila in df.iterrows():
#                     EmpleadoDotacion.objects.create(
#                         cedula=fila['NUMERO DE DOCUMENTO'],
#                         nombre=fila['NOMBRE COMPLETO'],
#                         ciudad=fila['SUCURSAL'],
#                         fecha_ingreso=pd.to_datetime(fila['INGRESO'], errors='coerce'),
#                         cargo=fila['CARGO'],
#                         cliente=fila['CLIENTE'],
#                         centro_costo=fila['C. COSTO'],
#                         sexo=fila['SEXO'],
#                         talla_camisa=fila['TALLA CAMISA'],
#                         cantidad_camisa=int(fila['CANTIDAD']),
#                         talla_pantalon=fila['TALLA PANTALON'],
#                         cantidad_pantalon=int(fila['CANTIDAD.1']),
#                         talla_zapatos=fila['TALLA ZAPATOS'],
#                         cantidad_zapatos=int(fila['CANTIDAD.2']),
#                         cantidad_botas_caucho=int(fila['BOTA CAUCHO'])
#                     )
#                 messages.success(request, "Empleados cargados correctamente.")
#                 return redirect('cargar_empleados')  # ajusta con el nombre correcto de tu URL
#             except Exception as e:
#                 messages.error(request, f"Error al procesar el archivo: {e}")
#     else:
#         form = CargarArchivoForm()

#     return render(request, 'cargar_empleados.html', {'form': form})

# import pandas as pd
# from django.shortcuts import render, redirect
# from django.http import HttpResponse, JsonResponse
# from django.contrib import messages
# from .forms import CargarArchivoForm
# from .models import EmpleadoDotacion
# from django.contrib.auth.decorators import login_required
from applications.inventario.models import  InventarioBodega
from django.utils import timezone
from decimal import Decimal
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils import timezone
import pandas as pd
from .models import EmpleadoDotacion, EntregaDotacion, DetalleEntregaDotacion
from applications.grupos_dotacion.models import GrupoDotacion, GrupoDotacionProducto
# from .models import Salida, ItemSalida
# from applications.inventario.models import Salida, ItemSalida
from applications.ordenes_salida.models import Salida, ItemSalida
from applications.bodegas.models import Bodega
from .forms import CargarArchivoForm
from .utils import safe_str, safe_int
from django.contrib.auth.decorators import login_required
import openpyxl
from django.db import transaction
from applications.productos.models import Producto
from applications.clientes.models import Cliente
from applications.inventario.models import InventarioBodega

from decimal import Decimal


@login_required
def historial_entregas(request):
    entregas = EntregaDotacion.objects.select_related('empleado', 'grupo') \
        .order_by('-fecha_entrega')
    return render(request, 'historial_entregas.html', {'entregas': entregas})


@login_required(login_url='login_usuario')
def empleadodotacion(request):
    #ciudades = list(Ciudad.objects.values())
    empleadoDotacion = EmpleadoDotacion.objects.all()
    return render(request, 'empleaDotacion.html', {
        'empleadoDotacion': empleadoDotacion
    })


@login_required(login_url='login_usuario')    
def list_empleados(_request):
    # def list_Cliente(request):
    empleadoDotacion =list(EmpleadoDotacion.objects.values())
    data={'empleadoDotacion':empleadoDotacion}
    return JsonResponse(data)
    # cliente = Cliente.objects.all()
    # data = {
    #     'cliente': [
    #         {
    #             'id_cliente': c.id_cliente,
    #             'nombre': c.nombre,
    #             'telefono': c.telefono,
    #             'email': c.email,
    #             'direccion': c.direccion,
    #             'id_ciudad': c.ciudad.nombre,  # <-- corregido
    #             'activo': c.activo,
    #             'url_editar': reverse('modificar_cliente', args=[c.id_cliente])
    #         } for c in cliente
    #     ]
    # }
    # return JsonResponse(data)      
    

def safe_str(value):
    return '' if pd.isna(value) else str(value).strip()


def safe_int(value):
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return 0


# def cargar_empleados_desde_excel(request):
#     if request.method == 'POST':
#         form = CargarArchivoForm(request.POST, request.FILES)
#         if form.is_valid():
#             archivo = request.FILES['archivo']
#             try:
#                 df = pd.read_excel(archivo)
                
#                 df.columns = df.columns.str.strip()  # Elimina espacios o saltos de línea
                
#                 df = pd.read_excel(archivo)
#                 df.columns = df.columns.str.strip()  # Limpia espacios

#                 # Asignar nombres únicos a columnas duplicadas
#                 df.columns.values[8] = 'CANTIDAD_CAMISA'
#                 df.columns.values[10] = 'CANTIDAD_PANTALON'
#                 df.columns.values[12] = 'CANTIDAD_ZAPATOS'

#                 # Renombrar columnas sucias o incorrectas
#                 df.rename(columns={
#                                 'NUMERO DE DO CUMENTO': 'NUMERO DE DOCUMENTO',
#                                 'CANTIDAD ': 'CANTIDAD_CAMISA',         # Aquí estaba la cantidad de camisa
#                                 'CANTIDAD': 'CANTIDAD_PANTALON',      # Aquí está la cantidad de pantalón
#                                 'CANTIDAD': 'CANTIDAD_ZAPATOS',
#                                 'Unnamed: 0': 'IGNORAR_1',
#                                 'Unnamed: 15': 'IGNORAR_2',
#                                 'Unnamed: 21': 'IGNORAR_3',
#                                 '   SUCURSAL': 'SUCURSAL'
#                             }, inplace=True)

#                 print("🧪 Columnas detectadas:", df.columns.tolist())
#                 print(df.head())  # Mostrar primeras filas para validar

#                 columnas_necesarias = [
#                     'IGNORAR_1', 'NOMBRE COMPLETO', 'SUCURSAL', 'INGRESO', 'CARGO', 'CLIENTE',
#                     'C. COSTO', 'SEXO', 'TALLA CAMISA', 'CANTIDAD_CAMISA',
#                     'TALLA PANTALON', 'CANTIDAD_PANTALON',
#                     'TALLA ZAPATOS', 'CANTIDAD_ZAPATOS', 'BOTA CAUCHO'
#                 ]

#                 faltantes = [col for col in columnas_necesarias if col not in df.columns]
#                 if faltantes:
#                     messages.error(request, f"❌ Faltan columnas en el archivo: {faltantes}")
#                     return render(request, 'cargar_empleados.html', {'form': form})

#                 contador = 0
#                 for _, fila in df.iterrows():
#                     cedula = safe_str(fila['NUMERO DE DOCUMENTO'])

#                     if EmpleadoDotacion.objects.filter(cedula=cedula).exists():
#                         continue  # Evitar duplicados

#                     EmpleadoDotacion.objects.create(
#                         cedula=cedula,
#                         nombre=safe_str(fila['NOMBRE COMPLETO']),
#                         ciudad=safe_str(fila['SUCURSAL']),
#                         fecha_ingreso=pd.to_datetime(fila['INGRESO'], errors='coerce'),
#                         cargo=safe_str(fila['CARGO']),
#                         cliente=safe_str(fila['CLIENTE']),
#                         centro_costo=safe_str(fila['C. COSTO']),
#                         sexo=safe_str(fila['SEXO']),
#                         talla_camisa=safe_str(fila['TALLA CAMISA']),
#                         cantidad_camisa=safe_int(fila['CANTIDAD_CAMISA']),
#                         talla_pantalon=safe_str(fila['TALLA PANTALON']),
#                         cantidad_pantalon=safe_int(fila['CANTIDAD_PANTALON']),
#                         talla_zapatos=safe_str(fila['TALLA ZAPATOS']),
#                         cantidad_zapatos=safe_int(fila['CANTIDAD_ZAPATOS']),
#                         cantidad_botas_caucho=safe_int(fila['BOTA CAUCHO']),
#                     )
#                     contador += 1

#                 if contador > 0:
#                     messages.success(request, f"✅ Se cargaron {contador} empleados correctamente.")
#                 else:
#                     messages.warning(request, "⚠️ No se cargó ningún empleado. Puede que ya existan.")

#                 return redirect('cargar_empleados')
#             except Exception as e:
#                 messages.error(request, f"❌ Error al procesar el archivo: {e}")
#     else:
#         form = CargarArchivoForm()

#     return render(request, 'cargar_empleados.html', {'form': form})


@login_required
def historial_entregas(request):
    entregas = EntregaDotacion.objects.select_related('empleado', 'grupo').order_by('-fecha_entrega')
    return render(request, 'historial_entregas.html', {'entregas': entregas})

# @login_required
# def cargar_empleados_desde_excel(request):
#     if request.method == 'POST':
#         form = CargarArchivoForm(request.POST, request.FILES)
#         if form.is_valid():
#             archivo = request.FILES['archivo']
#             try:
#                 df = pd.read_excel(archivo)
#                 df.columns = df.columns.str.strip()

#                 # Limpiar nombres de columnas
#                 df.columns.values[8] = 'CANTIDAD_CAMISA'
#                 df.columns.values[10] = 'CANTIDAD_PANTALON'
#                 df.columns.values[12] = 'CANTIDAD_ZAPATOS'

#                 df.rename(columns={
#                     'NUMERO DE DO CUMENTO': 'NUMERO DE DOCUMENTO',
#                     'CANTIDAD ': 'CANTIDAD_CAMISA',
#                     'CANTIDAD': 'CANTIDAD_PANTALON',
#                     'Unnamed: 0': 'IGNORAR_1',
#                     'Unnamed: 15': 'IGNORAR_2',
#                     'Unnamed: 21': 'IGNORAR_3',
#                     '   SUCURSAL': 'SUCURSAL'
#                 }, inplace=True)

#                 columnas_necesarias = [
#                     'NUMERO DE DOCUMENTO', 'NOMBRE COMPLETO', 'SUCURSAL', 'INGRESO', 'CARGO',
#                     'CLIENTE', 'C. COSTO', 'SEXO', 'TALLA CAMISA', 'CANTIDAD_CAMISA',
#                     'TALLA PANTALON', 'CANTIDAD_PANTALON', 'TALLA ZAPATOS',
#                     'CANTIDAD_ZAPATOS', 'BOTA CAUCHO'
#                 ]

#                 faltantes = [col for col in columnas_necesarias if col not in df.columns]
#                 if faltantes:
#                     messages.error(request, f"❌ Faltan columnas en el archivo: {faltantes}")
#                     return render(request, 'cargar_empleados.html', {'form': form})

#                 contador = 0
#                 entregas = 0
#                 empleados_sin_entrega = []

#                 for _, fila in df.iterrows():
#                     cedula = safe_str(fila['NUMERO DE DOCUMENTO']).strip()
#                     if EmpleadoDotacion.objects.filter(cedula=cedula).exists():
#                         continue

#                     # Limpieza de campos
#                     nombre = safe_str(fila['NOMBRE COMPLETO']).strip()
#                     ciudad = safe_str(fila['CENTRO TRABAJO']).strip().title()
#                     cargo = safe_str(fila['CARGO']).strip()
#                     cliente = safe_str(fila['CLIENTE']).strip()
#                     sexo = safe_str(fila['SEXO']).strip().upper()

#                     empleado_obj = EmpleadoDotacion.objects.create(
#                         cedula=cedula,
#                         nombre=nombre,
#                         ciudad=ciudad,
#                         fecha_ingreso=pd.to_datetime(fila['INGRESO'], errors='coerce'),
#                         cargo=cargo,
#                         cliente=cliente,
#                         centro_costo=safe_str(fila['C. COSTO']),
#                         sexo=sexo,
#                         talla_camisa=safe_str(fila['TALLA CAMISA']),
#                         cantidad_camisa=safe_int(fila['CANTIDAD_CAMISA']),
#                         talla_pantalon=safe_str(fila['TALLA PANTALON']),
#                         cantidad_pantalon=safe_int(fila['CANTIDAD_PANTALON']),
#                         talla_zapatos=safe_str(fila['TALLA ZAPATOS']),
#                         cantidad_zapatos=safe_int(fila['CANTIDAD_ZAPATOS']),
#                         cantidad_botas_caucho=safe_int(fila['BOTA CAUCHO']),
#                     )
#                     contador += 1

#                     grupos = GrupoDotacion.objects.filter(
#                         cargos__nombre__iexact=cargo,
#                         ciudades__nombre__iexact=ciudad,
#                         cliente__nombre__icontains=cliente,
#                         genero__iexact=sexo
#                     ).distinct()

#                     if grupos.exists():
#                         grupo = grupos.first()
#                         EntregaDotacion.objects.create(
#                             empleado=empleado_obj,
#                             grupo=grupo
#                         )
#                         entregas += 1
#                     else:
#                         motivo = f"{nombre} ({cedula}) - Sin grupo para Cargo: '{cargo}', Ciudad: '{ciudad}', Cliente: '{cliente}', Género: '{sexo}'"
#                         empleados_sin_entrega.append(motivo)

#                 if contador > 0:
#                     mensaje = f"✅ Se cargaron {contador} empleados y se generaron {entregas} entregas."
#                     if empleados_sin_entrega:
#                         mensaje += f" ⚠️ No se generó entrega para {len(empleados_sin_entrega)} empleados."
#                         request.session['empleados_sin_entrega'] = empleados_sin_entrega
#                     messages.success(request, mensaje)
#                 else:
#                     messages.warning(request, "⚠️ No se cargó ningún empleado. Puede que ya existan.")

#                 return redirect('cargar_empleados')

#             except Exception as e:
#                 messages.error(request, f"❌ Error al procesar el archivo: {e}")
#     else:
#         form = CargarArchivoForm()

#     empleados_sin_entrega = request.session.pop('empleados_sin_entrega', [])

#     return render(request, 'cargar_empleados.html', {
#         'form': form,
#         'empleados_sin_entrega': empleados_sin_entrega
#     })


# @login_required
# def cargar_empleados_desde_excel(request):
#     if request.method == 'POST':
#         form = CargarArchivoForm(request.POST, request.FILES)
#         if form.is_valid():
#             archivo = request.FILES['archivo']
#             try:
#                 df = pd.read_excel(archivo)
#                 df.columns = df.columns.str.strip()

#                 df.columns.values[8] = 'CANTIDAD_CAMISA'
#                 df.columns.values[10] = 'CANTIDAD_PANTALON'
#                 df.columns.values[12] = 'CANTIDAD_ZAPATOS'

#                 df.rename(columns={
#                     'NUMERO DE DO CUMENTO': 'NUMERO DE DOCUMENTO',
#                     'CANTIDAD ': 'CANTIDAD_CAMISA',
#                     'CANTIDAD': 'CANTIDAD_PANTALON',
#                     'Unnamed: 0': 'IGNORAR_1',
#                     'Unnamed: 15': 'IGNORAR_2',
#                     'Unnamed: 21': 'IGNORAR_3',
#                     '   SUCURSAL': 'SUCURSAL'
#                 }, inplace=True)

#                 columnas_necesarias = [
#                     'NUMERO DE DOCUMENTO', 'NOMBRE COMPLETO', 'SUCURSAL', 'INGRESO', 'CARGO',
#                     'CLIENTE', 'C. COSTO', 'SEXO', 'TALLA CAMISA', 'CANTIDAD_CAMISA',
#                     'TALLA PANTALON', 'CANTIDAD_PANTALON', 'TALLA ZAPATOS',
#                     'CANTIDAD_ZAPATOS', 'BOTA CAUCHO'
#                 ]

#                 faltantes = [col for col in columnas_necesarias if col not in df.columns]
#                 if faltantes:
#                     messages.error(request, f"❌ Faltan columnas en el archivo: {faltantes}")
#                     return render(request, 'cargar_empleados.html', {'form': form})

#                 contador = 0
#                 entregas = 0
#                 empleados_sin_entrega = []

#                 for _, fila in df.iterrows():
#                     cedula = safe_str(fila['NUMERO DE DOCUMENTO']).strip()
#                     if EmpleadoDotacion.objects.filter(cedula=cedula).exists():
#                         continue

#                     empleado_obj = EmpleadoDotacion.objects.create(
#                         cedula=cedula,
#                         nombre=safe_str(fila['NOMBRE COMPLETO']).strip(),
#                         ciudad=safe_str(fila['CENTRO TRABAJO']).strip().title(),
#                         fecha_ingreso=pd.to_datetime(fila['INGRESO'], errors='coerce'),
#                         cargo=safe_str(fila['CARGO']).strip(),
#                         cliente=safe_str(fila['CLIENTE']).strip(),
#                         centro_costo=safe_str(fila['C. COSTO']),
#                         sexo=safe_str(fila['SEXO']).strip().upper(),
#                         talla_camisa=safe_str(fila['TALLA CAMISA']),
#                         cantidad_camisa=safe_int(fila['CANTIDAD_CAMISA']),
#                         talla_pantalon=safe_str(fila['TALLA PANTALON']),
#                         cantidad_pantalon=safe_int(fila['CANTIDAD_PANTALON']),
#                         talla_zapatos=safe_str(fila['TALLA ZAPATOS']),
#                         cantidad_zapatos=safe_int(fila['CANTIDAD_ZAPATOS']),
#                         cantidad_botas_caucho=safe_int(fila['BOTA CAUCHO']),
#                     )
#                     contador += 1

#                     grupos = GrupoDotacion.objects.filter(
#                         cargos__nombre__iexact=empleado_obj.cargo,
#                         ciudades__nombre__iexact=empleado_obj.ciudad,
#                         cliente__nombre__icontains=empleado_obj.cliente,
#                         genero__iexact=empleado_obj.sexo
#                     ).distinct()

#                     if grupos.exists():
#                         grupo = grupos.first()
#                         entrega = EntregaDotacion.objects.create(
#                             empleado=empleado_obj,
#                             grupo=grupo
#                         )

#                         productos_grupo = GrupoDotacionProducto.objects.filter(grupo=grupo)
#                         for item in productos_grupo:
#                             DetalleEntregaDotacion.objects.create(
#                                 entrega=entrega,
#                                 producto=item.producto,
#                                 cantidad=item.cantidad
#                             )
#                         entregas += 1
#                     else:
#                         motivo = f"{empleado_obj.nombre} ({cedula}) - Sin grupo para Cargo: '{empleado_obj.cargo}', Ciudad: '{empleado_obj.ciudad}', Cliente: '{empleado_obj.cliente}', Género: '{empleado_obj.sexo}'"
#                         empleados_sin_entrega.append(motivo)

#                 if contador > 0:
#                     mensaje = f"✅ Se cargaron {contador} empleados y se generaron {entregas} entregas."
#                     if empleados_sin_entrega:
#                         mensaje += f" ⚠️ No se generó entrega para {len(empleados_sin_entrega)} empleados."
#                         request.session['empleados_sin_entrega'] = empleados_sin_entrega
#                     messages.success(request, mensaje)
#                 else:
#                     messages.warning(request, "⚠️ No se cargó ningún empleado. Puede que ya existan.")

#                 return redirect('cargar_empleados')

#             except Exception as e:
#                 messages.error(request, f"❌ Error al procesar el archivo: {e}")
#     else:
#         form = CargarArchivoForm()

#     empleados_sin_entrega = request.session.pop('empleados_sin_entrega', [])

#     return render(request, 'cargar_empleados.html', {
#         'form': form,
#         'empleados_sin_entrega': empleados_sin_entrega
#     })


# from django.contrib import messages
# from django.shortcuts import render, redirect
# from django.utils import timezone
# from django.contrib.auth.decorators import login_required
# import pandas as pd

# from .forms import CargarArchivoForm
# from .models import EmpleadoDotacion, EntregaDotacion, DetalleEntregaDotacion
# from applications.dotacion.models import GrupoDotacion, GrupoDotacionProducto

# from utils.helpers import safe_str, safe_int  # Asumo que ya tienes helpers para limpiar strings y números


# @login_required
# def cargar_empleados_desde_excel(request):
#     if request.method == 'POST':
#         form = CargarArchivoForm(request.POST, request.FILES)
#         if form.is_valid():
#             archivo = request.FILES['archivo']
#             try:
#                 df = pd.read_excel(archivo)
#                 df.columns = df.columns.str.strip()

#                 # Renombrar columnas según estructura del Excel
#                 df.columns.values[8] = 'CANTIDAD_CAMISA'
#                 df.columns.values[10] = 'CANTIDAD_PANTALON'
#                 df.columns.values[12] = 'CANTIDAD_ZAPATOS'

#                 df.rename(columns={
#                     'NUMERO DE DO CUMENTO': 'NUMERO DE DOCUMENTO',
#                     'CANTIDAD ': 'CANTIDAD_CAMISA',
#                     'CANTIDAD': 'CANTIDAD_PANTALON',
#                     'Unnamed: 0': 'IGNORAR_1',
#                     'Unnamed: 15': 'IGNORAR_2',
#                     'Unnamed: 21': 'IGNORAR_3',
#                     '   SUCURSAL': 'SUCURSAL'
#                 }, inplace=True)

#                 columnas_necesarias = [
#                     'NUMERO DE DOCUMENTO', 'NOMBRE COMPLETO', 'CENTRO TRABAJO', 'INGRESO', 'CARGO',
#                     'CLIENTE', 'C. COSTO', 'SEXO', 'TALLA CAMISA', 'CANTIDAD_CAMISA',
#                     'TALLA PANTALON', 'CANTIDAD_PANTALON', 'TALLA ZAPATOS',
#                     'CANTIDAD_ZAPATOS', 'BOTA CAUCHO'
#                 ]
#                 faltantes = [col for col in columnas_necesarias if col not in df.columns]
#                 if faltantes:
#                     messages.error(request, f"❌ Faltan columnas en el archivo: {faltantes}")
#                     return render(request, 'cargar_empleados.html', {'form': form})

#                 contador = 0
#                 entregas = 0
#                 empleados_sin_entrega = []
#                 bodega_dotacion = Bodega.objects.get(nombre__iexact="Principal")

#                 for _, fila in df.iterrows():
#                     cedula = safe_str(fila['NUMERO DE DOCUMENTO']).strip()
#                     if EmpleadoDotacion.objects.filter(cedula=cedula).exists():
#                         continue

#                     empleado_obj = EmpleadoDotacion.objects.create(
#                         cedula=cedula,
#                         nombre=safe_str(fila['NOMBRE COMPLETO']).strip(),
#                         ciudad=safe_str(fila['SUCURSAL']).strip().title(),
#                         fecha_ingreso=pd.to_datetime(fila['INGRESO'], errors='coerce'),
#                         cargo=safe_str(fila['CARGO']).strip(),
#                         cliente=safe_str(fila['CLIENTE']).strip(),
#                         centro_costo=safe_str(fila['C. COSTO']),
#                         sexo=safe_str(fila['SEXO']).strip().upper(),
#                         talla_camisa=safe_str(fila['TALLA CAMISA']),
#                         cantidad_camisa=safe_int(fila['CANTIDAD_CAMISA']),
#                         talla_pantalon=safe_str(fila['TALLA PANTALON']),
#                         cantidad_pantalon=safe_int(fila['CANTIDAD_PANTALON']),
#                         talla_zapatos=safe_str(fila['TALLA ZAPATOS']),
#                         cantidad_zapatos=safe_int(fila['CANTIDAD_ZAPATOS']),
#                         cantidad_botas_caucho=safe_int(fila['BOTA CAUCHO']),
#                     )
#                     contador += 1

#                     grupos = GrupoDotacion.objects.filter(
#                         cargos__nombre__iexact=empleado_obj.cargo,
#                         ciudades__nombre__iexact=empleado_obj.ciudad,
#                         cliente__nombre__icontains=empleado_obj.cliente,
#                         genero__iexact=empleado_obj.sexo
#                     ).distinct()

#                     if grupos.exists():
#                         grupo = grupos.first()

#                         # Crear la entrega
#                         entrega = EntregaDotacion.objects.create(
#                             empleado=empleado_obj,
#                             grupo=grupo
#                         )

#                         # Crear salida de inventario
#                         salida = Salida.objects.create(
#                             tipo_documento="ED",
#                             numero_documento=f"DOT-{entrega.id}",
#                             fecha=timezone.now(),
#                             bodegaSalida=bodega_dotacion,
#                             observaciones=f"Entrega automática para {empleado_obj.nombre}",
#                             responsable=request.user
#                         )

#                         productos_grupo = GrupoDotacionProducto.objects.filter(grupo=grupo)
#                         for item in productos_grupo:
#                             # Detalle entrega
#                             DetalleEntregaDotacion.objects.create(
#                                 entrega=entrega,
#                                 producto=item.producto,
#                                 cantidad=item.cantidad
#                             )

#                             # Salida de inventario
#                             ItemSalida.objects.create(
#                                 salida=salida,
#                                 producto=item.producto,
#                                 cantidad=item.cantidad
#                             )

#                         entregas += 1
#                     else:
#                         motivo = (
#                             f"{empleado_obj.nombre} ({cedula}) - Sin grupo para Cargo: '{empleado_obj.cargo}', "
#                             f"Ciudad: '{empleado_obj.ciudad}', Cliente: '{empleado_obj.cliente}', "
#                             f"Género: '{empleado_obj.sexo}'"
#                         )
#                         empleados_sin_entrega.append(motivo)

#                 if contador > 0:
#                     mensaje = f"✅ Se cargaron {contador} empleados y se generaron {entregas} entregas."
#                     if empleados_sin_entrega:
#                         mensaje += f" ⚠️ No se generó entrega para {len(empleados_sin_entrega)} empleados."
#                         request.session['empleados_sin_entrega'] = empleados_sin_entrega
#                     messages.success(request, mensaje)
#                 else:
#                     messages.warning(request, "⚠️ No se cargó ningún empleado. Puede que ya existan.")

#                 return redirect('cargar_empleados')

#             except Exception as e:
#                 messages.error(request, f"❌ Error al procesar el archivo: {e}")
#     else:
#         form = CargarArchivoForm()

#     empleados_sin_entrega = request.session.pop('empleados_sin_entrega', [])

#     return render(request, 'cargar_empleados.html', {
#         'form': form,
#         'empleados_sin_entrega': empleados_sin_entrega
#     })


# Función auxiliar para crear la salida
def generar_salida_por_entrega(entrega, productos_entregados, usuario):
    bodega = Bodega.objects.get(nombre__iexact="Principal")
    
    salida = Salida.objects.create(
        tipo_documento='ED',
        # cliente=entrega.empleado.cliente,
        cliente=Cliente.objects.get(nombre__icontains=entrega.empleado.cliente),
        observaciones=f"Entrega automática para {entrega.empleado.nombre}",
        bodegaSalida=bodega,
        usuario_creador=usuario,
        total=Decimal("0.00")
    )

    for detalle in productos_entregados:
        ItemSalida.objects.create(
            salida=salida,
            producto=detalle.producto,
            cantidad=detalle.cantidad
        )



@login_required
def cargar_empleados_desde_excel(request):
    if request.method == 'POST':
        form = CargarArchivoForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo']
            try:
                df = pd.read_excel(archivo)
                df.columns = df.columns.str.strip()

                # Renombrar columnas según índices conocidos
                try:
                    df.columns.values[8] = 'CANTIDAD_CAMISA'
                    df.columns.values[10] = 'CANTIDAD_PANTALON'
                    df.columns.values[12] = 'CANTIDAD_ZAPATOS'
                except IndexError:
                    messages.error(request, "❌ El archivo no tiene suficientes columnas.")
                    return render(request, 'cargar_empleados.html', {'form': form})

                df.rename(columns={
                    'NUMERO DE DO CUMENTO': 'NUMERO DE DOCUMENTO',
                    'CANTIDAD ': 'CANTIDAD_CAMISA',
                    'CANTIDAD': 'CANTIDAD_PANTALON',
                    'Unnamed: 0': 'IGNORAR_1',
                    'Unnamed: 15': 'IGNORAR_2',
                    'Unnamed: 21': 'IGNORAR_3',
                    '   SUCURSAL': 'SUCURSAL'
                }, inplace=True)

                columnas_requeridas = [
                    'NUMERO DE DOCUMENTO', 'NOMBRE COMPLETO', 'CENTRO TRABAJO', 'INGRESO', 'CARGO',
                    'CLIENTE', 'C. COSTO', 'SEXO', 'TALLA CAMISA', 'CANTIDAD_CAMISA',
                    'TALLA PANTALON', 'CANTIDAD_PANTALON', 'TALLA ZAPATOS',
                    'CANTIDAD_ZAPATOS', 'BOTA CAUCHO'
                ]
                faltantes = [col for col in columnas_requeridas if col not in df.columns]
                if faltantes:
                    messages.error(request, f"❌ Faltan columnas en el archivo: {faltantes}")
                    return render(request, 'cargar_empleados.html', {'form': form})

                contador, entregas = 0, 0
                empleados_sin_entrega = []

                try:
                    bodega_dotacion = Bodega.objects.get(nombre__iexact="Principal")
                except Bodega.DoesNotExist:
                    messages.error(request, "❌ No se encontró la bodega 'Principal'.")
                    return render(request, 'cargar_empleados.html', {'form': form})

                for _, fila in df.iterrows():
                    cedula = safe_str(fila['NUMERO DE DOCUMENTO']).strip()
                    if EmpleadoDotacion.objects.filter(cedula=cedula).exists():
                        continue

                    empleado = EmpleadoDotacion.objects.create(
                        cedula=cedula,
                        nombre=safe_str(fila['NOMBRE COMPLETO']),
                        ciudad=safe_str(fila['CENTRO TRABAJO']).title(),
                        fecha_ingreso=pd.to_datetime(fila['INGRESO'], errors='coerce'),
                        cargo=safe_str(fila['CARGO']),
                        cliente=safe_str(fila['CLIENTE']),
                        centro_costo=safe_str(fila['C. COSTO']),
                        sexo=safe_str(fila['SEXO']).upper(),
                        talla_camisa=safe_str(fila['TALLA CAMISA']),
                        cantidad_camisa=safe_int(fila['CANTIDAD_CAMISA']),
                        talla_pantalon=safe_str(fila['TALLA PANTALON']),
                        cantidad_pantalon=safe_int(fila['CANTIDAD_PANTALON']),
                        talla_zapatos=safe_str(fila['TALLA ZAPATOS']),
                        cantidad_zapatos=safe_int(fila['CANTIDAD_ZAPATOS']),
                        cantidad_botas_caucho=safe_int(fila['BOTA CAUCHO']),
                    )
                    contador += 1

                    grupos = GrupoDotacion.objects.filter(
                        cargos__nombre__iexact=empleado.cargo,
                        ciudades__nombre__iexact=empleado.ciudad,
                        cliente__nombre__icontains=empleado.cliente,
                        genero__iexact=empleado.sexo
                    ).distinct()

                    if grupos.exists():
                        grupo = grupos.first()
                        entrega = EntregaDotacion.objects.create(empleado=empleado, grupo=grupo)

                        productos_entregados = []
                        productos = GrupoDotacionProducto.objects.filter(grupo=grupo)
                        for producto_grupo in productos:
                            detalle = DetalleEntregaDotacion.objects.create(
                                entrega=entrega,
                                producto=producto_grupo.producto,
                                cantidad=producto_grupo.cantidad
                            )
                            productos_entregados.append(detalle)

                        # Generar salida e ítems de salida
                        generar_salida_por_entrega(entrega, productos_entregados, request.user)

                        entregas += 1
                    else:
                        empleados_sin_entrega.append(
                            f"{empleado.nombre} ({empleado.cedula}) - Sin grupo para Cargo: '{empleado.cargo}', "
                            f"Ciudad: '{empleado.ciudad}', Cliente: '{empleado.cliente}', Género: '{empleado.sexo}'"
                        )
                        
                    # Generar salida e ítems de salida
                    generar_salida_por_entrega(entrega, productos_entregados, request.user)    

                if contador > 0:
                    mensaje = f"✅ Se cargaron {contador} empleados y se generaron {entregas} entregas."
                    if empleados_sin_entrega:
                        mensaje += f" ⚠️ No se generó entrega para {len(empleados_sin_entrega)} empleados."
                        request.session['empleados_sin_entrega'] = empleados_sin_entrega
                    messages.success(request, mensaje)
                else:
                    messages.warning(request, "⚠️ No se cargó ningún empleado nuevo.")

                return redirect('cargar_empleados')

            except Exception as e:
                messages.error(request, f"❌ Error al procesar el archivo: {str(e)}")

    else:
        form = CargarArchivoForm()

    empleados_sin_entrega = request.session.pop('empleados_sin_entrega', [])

    return render(request, 'cargar_empleados.html', {
        'form': form,
        'empleados_sin_entrega': empleados_sin_entrega
    })



# Vista para cargar empleados desde archivo
# @transaction.atomic
# def cargar_empleados_desde_excel(request):
#     if request.method == 'POST' and request.FILES.get('archivo_excel'):
#         archivo = request.FILES['archivo_excel']

#         try:
#             wb = openpyxl.load_workbook(archivo)
#             hoja = wb.active

#             empleados_cargados = 0
#             entregas_generadas = 0
#             empleados_sin_grupo = []

#             for fila in hoja.iter_rows(min_row=2, values_only=True):
#                 cedula, nombre, ciudad, fecha_ingreso, cargo, cliente, centro_costo, sexo, talla, cantidad = fila

#                 if EmpleadoDotacion.objects.filter(cedula=cedula).exists():
#                     continue  # Saltar si ya existe

#                 empleado = EmpleadoDotacion.objects.create(
#                     cedula=cedula,
#                     nombre=nombre,
#                     ciudad=ciudad,
#                     fecha_ingreso=fecha_ingreso,
#                     cargo=cargo,
#                     cliente=cliente,
#                     centro_costo=centro_costo,
#                     sexo=sexo,
#                     talla=talla,
#                     cantidad=cantidad
#                 )
#                 empleados_cargados += 1

#                 # Buscar grupo de dotación asociado
#                 grupo_dotacion = GrupoDotacion.objects.filter(
#                     ciudad__iexact=ciudad,
#                     cargo__nombre__iexact=cargo,
#                     cliente__nombre__iexact=cliente,
#                     genero__iexact=sexo
#                 ).first()

#                 if not grupo_dotacion:
#                     empleados_sin_grupo.append(empleado)
#                     continue

#                 # Crear entrega
#                 entrega = EntregaDotacion.objects.create(
#                     empleado=empleado,
#                     grupo=grupo_dotacion,
#                     fecha_entrega=timezone.now(),
#                     observaciones="Entrega generada automáticamente desde archivo"
#                 )

#                 # Crear los productos entregados
#                 productos_entregados = []
#                 for item in grupo_dotacion.productos.all():
#                     detalle = DetalleEntregaDotacion.objects.create(
#                         entrega=entrega,
#                         producto=item.producto,
#                         cantidad=item.cantidad
#                     )
#                     productos_entregados.append(detalle)

#                 # Generar salida e ítems de salida
#                 generar_salida_por_entrega(entrega, productos_entregados, request.user)

#                 entregas_generadas += 1

#             mensajes = [f"✅ Se cargaron {empleados_cargados} empleados y se generaron {entregas_generadas} entregas."]
#             if empleados_sin_grupo:
#                 mensajes.append(f"⚠️ No se generó entrega para {len(empleados_sin_grupo)} empleados.")

#             messages.success(request, " ".join(mensajes))
#             return redirect('nombre_de_tu_template_o_url')

#         except Exception as e:
#             messages.error(request, f"❌ Error al procesar el archivo: {e}")
#             return redirect('cargar_empleados.html')

#     return render(request, 'cargar_empleados.html')
