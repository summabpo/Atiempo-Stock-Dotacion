
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
from django.shortcuts import render, redirect, get_object_or_404
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
from applications.ciudades.models import Ciudad
from applications.grupos_dotacion.models import Cargo
from .forms import CargarArchivoForm
from .utils import safe_str, safe_int, generar_formato_entrega_pdf
from django.contrib.auth.decorators import login_required
import openpyxl
from django.db import transaction
from applications.productos.models import Producto
from applications.clientes.models import Cliente
from applications.inventario.models import InventarioBodega
from openpyxl import load_workbook
from io import BytesIO
from django.utils.timezone import now
#from dotacionAT.middleware import get_current_user
from crum import set_current_user, get_current_user
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import datetime
from decimal import Decimal


def get_or_none(modelo, **filtros):
    try:
        return modelo.objects.get(**filtros)
    except modelo.DoesNotExist:
        return None

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
    # empleadoDotacion =list(EmpleadoDotacion.objects.values())
    # data={'empleadoDotacion':empleadoDotacion}
    # return JsonResponse(data)
    empleadoDotacion = EmpleadoDotacion.objects.all()
    data = {
        'empleado': [
            {
                'cedula': c.cedula,
                'nombre': c.nombre,
                'ciudad': c.ciudad,
                'cargo': c.cargo,
                'cliente': c.cliente.nombre if c.cliente else '',
                'centro_costo': c.centro_costo,  # <-- corregido
                'Genero': c.sexo,
                'fecha_ingreso': c.fecha_ingreso,
                'fecha_registro': c.fecha_registro
            } for c in empleadoDotacion
        ]
    }
    return JsonResponse(data)      
    

def safe_str(value):
    return str(value).strip().upper() if pd.notnull(value) else ''

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
    print("🧪 Usuario recibido:", usuario)
    print("🧪 Tipo del usuario recibido:", type(usuario))
    if not hasattr(usuario, "is_authenticated"):
        raise ValueError(f"🛑 El parámetro 'usuario' debe ser un User, no {type(usuario)}")
    
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



#@login_required
# def cargar_empleados_desde_excel(request):
#     if request.method == 'POST':
#         form = CargarArchivoForm(request.POST, request.FILES)
#         if form.is_valid():
#             archivo = request.FILES['archivo']
#             try:
#                 df = pd.read_excel(archivo)
#                 df.columns = df.columns.str.strip()

#                 # Renombrar columnas según índices conocidos
#                 try:
#                     df.columns.values[8] = 'CANTIDAD_CAMISA'
#                     df.columns.values[10] = 'CANTIDAD_PANTALON'
#                     df.columns.values[12] = 'CANTIDAD_ZAPATOS'
#                 except IndexError:
#                     messages.error(request, "❌ El archivo no tiene suficientes columnas.")
#                     return render(request, 'cargar_empleados.html', {'form': form})

#                 df.rename(columns={
#                     'NUMERO DE DO CUMENTO': 'NUMERO DE DOCUMENTO',
#                     'CANTIDAD ': 'CANTIDAD_CAMISA',
#                     'CANTIDAD': 'CANTIDAD_PANTALON',
#                     'Unnamed: 0': 'IGNORAR_1',
#                     'Unnamed: 15': 'IGNORAR_2',
#                     'Unnamed: 21': 'IGNORAR_3',
#                     '   SUCURSAL': 'SUCURSAL'
#                 }, inplace=True)

#                 columnas_requeridas = [
#                     'NUMERO DE DOCUMENTO', 'NOMBRE COMPLETO', 'CENTRO TRABAJO', 'INGRESO', 'CARGO',
#                     'CLIENTE', 'C. COSTO', 'SEXO', 'TALLA CAMISA', 'CANTIDAD_CAMISA',
#                     'TALLA PANTALON', 'CANTIDAD_PANTALON', 'TALLA ZAPATOS',
#                     'CANTIDAD_ZAPATOS', 'BOTA CAUCHO'
#                 ]
#                 faltantes = [col for col in columnas_requeridas if col not in df.columns]
#                 if faltantes:
#                     messages.error(request, f"❌ Faltan columnas en el archivo: {faltantes}")
#                     return render(request, 'cargar_empleados.html', {'form': form})

#                 contador, entregas = 0, 0
#                 empleados_sin_entrega = []

#                 try:
#                     bodega_dotacion = Bodega.objects.get(nombre__iexact="Principal")
#                 except Bodega.DoesNotExist:
#                     messages.error(request, "❌ No se encontró la bodega 'Principal'.")
#                     return render(request, 'cargar_empleados.html', {'form': form})

#                 for _, fila in df.iterrows():
#                     cedula = safe_str(fila['NUMERO DE DOCUMENTO']).strip()
#                     if EmpleadoDotacion.objects.filter(cedula=cedula).exists():
#                         continue
                    
#                     # Obtener o crear instancias reales
#                     cliente, _ = Cliente.objects.get_or_create(nombre=safe_str(fila['CLIENTE']).strip())
#                     ciudad, _ = Ciudad.objects.get_or_create(nombre=safe_str(fila['CENTRO TRABAJO']).strip().title())
#                     cargo, _ = Cargo.objects.get_or_create(nombre=safe_str(fila['CARGO']).strip())
#                     centro_costo = safe_str(fila['C. COSTO']).strip()

#                     # empleado = EmpleadoDotacion.objects.create(
#                     #     cedula=cedula,
#                     #     nombre=safe_str(fila['NOMBRE COMPLETO']),
#                     #     ciudad=safe_str(fila['CENTRO TRABAJO']).title(),
#                     #     fecha_ingreso=pd.to_datetime(fila['INGRESO'], errors='coerce'),
#                     #     cargo=safe_str(fila['CARGO']),
#                     #     cliente=safe_str(fila['CLIENTE']),
#                     #     centro_costo=safe_str(fila['C. COSTO']),
#                     #     sexo=safe_str(fila['SEXO']).upper(),
#                     #     talla_camisa=safe_str(fila['TALLA CAMISA']),
#                     #     cantidad_camisa=safe_int(fila['CANTIDAD_CAMISA']),
#                     #     talla_pantalon=safe_str(fila['TALLA PANTALON']),
#                     #     cantidad_pantalon=safe_int(fila['CANTIDAD_PANTALON']),
#                     #     talla_zapatos=safe_str(fila['TALLA ZAPATOS']),
#                     #     cantidad_zapatos=safe_int(fila['CANTIDAD_ZAPATOS']),
#                     #     cantidad_botas_caucho=safe_int(fila['BOTA CAUCHO']),
#                     # )
#                     empleado = EmpleadoDotacion.objects.create(
#                         cedula=cedula,
#                         nombre=safe_str(fila['NOMBRE COMPLETO']),
#                         ciudad=ciudad,
#                         fecha_ingreso=pd.to_datetime(fila['INGRESO'], errors='coerce'),
#                         cargo=cargo,
#                         cliente=cliente,
#                         centro_costo=centro_costo,
#                         sexo=safe_str(fila['SEXO']).upper(),
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
#                         cargos__nombre__iexact=empleado.cargo,
#                         ciudades__nombre__iexact=empleado.ciudad,
#                         cliente__nombre__icontains=empleado.cliente,
#                         genero__iexact=empleado.sexo
#                     ).distinct()
                    
#                     genero = safe_str(fila['SEXO']).upper()

#                     if grupos.exists():
#                         grupo = grupos.first()
#                         productos = GrupoDotacionProducto.objects.filter(grupo=grupo)

#                         # Validar stock
#                         productos_sin_stock = []
#                         for producto_grupo in productos:
#                             try:
#                                 inventario = InventarioBodega.objects.get(bodega=bodega_dotacion, producto=producto_grupo.producto)
#                                 if inventario.stock < producto_grupo.cantidad:
#                                     productos_sin_stock.append(producto_grupo.producto.nombre)
#                             except InventarioBodega.DoesNotExist:
#                                 productos_sin_stock.append(producto_grupo.producto.nombre)

#                         if productos_sin_stock:
#                             mensaje = f"{empleado.nombre} ({cedula}) - Sin stock para productos: {', '.join(productos_sin_stock)}"
#                             empleados_sin_entrega.append(mensaje)
#                             continue  # Saltar a la siguiente fila sin generar entrega

#                         # Si hay stock suficiente, generar entrega
#                         entrega = EntregaDotacion.objects.create(empleado=empleado, grupo=grupo)

#                         productos_entregados = []
#                         for producto_grupo in productos:
#                             detalle = DetalleEntregaDotacion.objects.create(
#                                 entrega=entrega,
#                                 producto=producto_grupo.producto,
#                                 cantidad=producto_grupo.cantidad
#                             )
#                             productos_entregados.append(detalle)

#                         # Generar salida e ítems de salida
#                         generar_salida_por_entrega(entrega, productos_entregados, request.user)

#                         entregas += 1
#                     else:
#                         errores = []
#                         if not GrupoDotacion.objects.filter(cargos=cargo).exists():
#                             errores.append(f"Cargo: '{cargo.nombre}'")
#                         if not GrupoDotacion.objects.filter(cliente=cliente).exists():
#                             errores.append(f"Cliente: '{cliente.nombre}'")
#                         if not GrupoDotacion.objects.filter(ciudades=ciudad).exists():
#                             errores.append(f"Ciudad: '{ciudad.nombre}'")
#                         if not GrupoDotacion.objects.filter(genero=genero).exists():
#                             errores.append(f"Género: '{genero}'")

#                         motivo = ', '.join(errores)
#                         mensaje = f"{empleado.nombre} ({cedula}) - Sin grupo para {motivo}"
#                         empleados_sin_entrega.append(mensaje)
#                         # empleados_sin_entrega.append(
#                         #     f"{empleado.nombre} ({empleado.cedula}) - Sin grupo para Cargo: '{empleado.cargo}', "
#                         #     f"Ciudad: '{empleado.ciudad}', Cliente: '{empleado.cliente}', Género: '{empleado.sexo}'"
#                         # )
                        
#                     # Generar salida e ítems de salida
#                     generar_salida_por_entrega(entrega, productos_entregados, request.user)    

#                 if contador > 0:
#                     mensaje = f"✅ Se cargaron {contador} empleados y se generaron {entregas} entregas."
#                     if empleados_sin_entrega:
#                         mensaje += f" ⚠️ No se generó entrega para {len(empleados_sin_entrega)} empleados."
#                         request.session['empleados_sin_entrega'] = empleados_sin_entrega
#                     messages.success(request, mensaje)
#                 else:
#                     messages.warning(request, "⚠️ No se cargó ningún empleado nuevo.")

#                 return redirect('cargar_empleados')

#             except Exception as e:
#                 messages.error(request, f"❌ Error al procesar el archivo: {str(e)}")

#     else:
#         form = CargarArchivoForm()

#     empleados_sin_entrega = request.session.pop('empleados_sin_entrega', [])

#     return render(request, 'cargar_empleados.html', {
#         'form': form,
#         'empleados_sin_entrega': empleados_sin_entrega
#     })


def obtener_talla_para_categoria(categoria, empleado):
    print(categoria)
    print(empleado)
    nombre = categoria.nombre.lower()
    if "camisa" in nombre:
        return empleado.talla_camisa
    elif "jean" in nombre or "pantalón" in nombre:
        return empleado.talla_pantalon
    elif "zapato" in nombre or "botas" in nombre or "bota" in nombre:
        return empleado.talla_zapatos
    return None


def safe_str_number(value):
    """Convierte un valor a string limpio, sin '.0' si es número."""
    if pd.isna(value) or value is None:
        return ""
    value_str = str(value).strip()
    if value_str.endswith(".0"):
        value_str = value_str[:-2]  # quita los dos últimos caracteres
    return value_str

def safe_date(value):
    """Convierte un valor a date o None."""
    if pd.isna(value) or value is None or str(value).strip() == "":
        return None
    if isinstance(value, pd.Timestamp):
        return value.date()
    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None
    
def normalizar_talla(talla, categoria=None):
    """
    Limpia y normaliza la talla según la categoría del producto.
    - Zapatos: extrae solo el número (N° 39 → 39)
    - Camisa / Pantalón: mayúsculas y sin espacios (m → M)
    - Otros: deja el valor limpio
    """
    if not isinstance(talla, str):
        talla = str(talla) if talla is not None else ""

    talla = talla.strip()

    if categoria:
        cat = categoria.strip().lower()
        if "zapato" in cat or "calzado" in cat:
            # Extraer solo dígitos de la talla
            import re
            match = re.search(r'\d+', talla)
            return match.group(0) if match else talla
        elif "CAMISA" in cat or "JEAN" in cat or "PANTALON" in cat:
            return talla.upper().replace(" ", "")
    return talla.upper()    
    
    

def cargar_empleados_desde_excel(request):
    if request.method == 'POST':
        set_current_user(request.user) 
        form = CargarArchivoForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo']
            print("📂 Archivo recibido:", archivo.name)
            try:
                df = pd.read_excel(archivo)  # ← Leemos el archivo
                df.columns = [col.strip().upper().replace(" ", "_") for col in df.columns]  # ← Normalizamos las columnas
                
                

                df.rename(columns={
                    'NUMERO DE DO CUMENTO': 'NUMERO DE DOCUMENTO',
                    # 'CANTIDAD ': 'CANTIDAD_CAMISA',
                    # 'CANTIDAD': 'CANTIDAD_PANTALON',
                    'Unnamed: 0': 'IGNORAR_1',
                    'Unnamed: 15': 'IGNORAR_2',
                    'Unnamed: 21': 'IGNORAR_3',
                    '   SUCURSAL': 'SUCURSAL'
                }, inplace=True)
                
               

                columnas_requeridas = [
                    'NUMERO_DE_DOCUMENTO', 'NOMBRE_COMPLETO', 'CENTRO_TRABAJO', 'INGRESO', 'CARGO',
                    'CLIENTE', 'C._COSTO', 'SEXO', 'TALLA_CAMISA', 'TALLA_PANTALON', 'TALLA_ZAPATOS'
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
                    cedula = safe_str(fila['NUMERO_DE_DOCUMENTO']).strip()
                    print("\n🆕 Procesando fila:", cedula)
                    if EmpleadoDotacion.objects.filter(cedula=cedula).exists():
                        continue
                    
                                       
                    cliente, _ = Cliente.objects.get_or_create(nombre=safe_str(fila['CLIENTE']).strip())
                    ciudad, _ = Ciudad.objects.get_or_create(nombre=safe_str(fila['CENTRO_TRABAJO']).strip().title())
                    cargo, _ = Cargo.objects.get_or_create(nombre=safe_str(fila['CARGO']).strip())
                    centro_costo = safe_str(fila['C._COSTO']).strip()
                    
                    
                    
                    fecha_ingreso = pd.to_datetime(fila['INGRESO'], errors='coerce')
                    if pd.isna(fecha_ingreso):
                        fecha_ingreso = None  # o una fecha por defecto
                    else:
                        fecha_ingreso = fecha_ingreso.date()
                    
                    talla_camisa = normalizar_talla(fila['TALLA_CAMISA'], categoria="CAMISA")
                    talla_pantalon = normalizar_talla(fila['TALLA_PANTALON'], categoria="PANTALON")
                    talla_zapatos = normalizar_talla(fila['TALLA_ZAPATOS'], categoria="BOTAS")
                    
                    empleado = EmpleadoDotacion.objects.create(
                    cedula=safe_str_number(fila['NUMERO_DE_DOCUMENTO']),
                    nombre=safe_str(fila['NOMBRE_COMPLETO']),
                    ciudad=safe_str(fila['CENTRO_TRABAJO']),  # Texto directo
                    fecha_ingreso = fecha_ingreso,
                    cargo=safe_str(fila['CARGO']),
                    cliente=safe_str(fila['CLIENTE']),  # Texto directo
                    centro_costo=safe_str(fila['C._COSTO']),
                    sexo=safe_str(fila['SEXO']),
                    #talla_camisa=safe_str(fila['TALLA_CAMISA']),
                    talla_camisa=talla_camisa,
                    cantidad_camisa=int(fila.get('CANTIDAD_CAMISA', 0) or 0),
                    #talla_pantalon=safe_str(fila['TALLA_PANTALON']),
                    talla_pantalon=talla_pantalon,
                    cantidad_pantalon=int(fila.get('CANTIDAD_PANTALON', 0) or 0),
                    #talla_zapatos=safe_str(fila['TALLA_ZAPATOS']),
                    talla_zapatos=talla_zapatos,
                    cantidad_zapatos=int(fila.get('CANTIDAD_ZAPATOS', 0) or 0),
                    cantidad_botas_caucho=int(fila.get('BOTAS_CAUCHO', 0) or 0),
                )
                    
                    contador += 1

                              
                    cargo_obj = Cargo.objects.get(nombre__iexact=empleado.cargo)
                    grupos = GrupoDotacion.objects.filter(
                        cargos=cargo_obj,
                        ciudades__nombre__iexact=empleado.ciudad,
                        cliente__nombre__icontains=empleado.cliente,
                        genero__iexact=empleado.sexo
                    ).distinct()

                    genero = safe_str(fila['SEXO']).upper()

                    if grupos.exists():
                        grupo = grupos.first()
                        productos = GrupoDotacionProducto.objects.filter(grupo=grupo)

                        productos_sin_stock = []
                        productos_entregados = []

                        for producto_grupo in productos:
                            talla = obtener_talla_para_categoria(producto_grupo.categoria, empleado)

                            try:
                                producto = Producto.objects.get(nombre__icontains=talla, categoria=producto_grupo.categoria)
                                inventario = InventarioBodega.objects.get(bodega=bodega_dotacion, producto=producto)

                                if inventario.stock < producto_grupo.cantidad:
                                    productos_sin_stock.append(producto.nombre)
                                    continue

                                entrega = EntregaDotacion.objects.get_or_create(empleado=empleado, grupo=grupo)[0]
                                detalle = DetalleEntregaDotacion.objects.create(
                                    entrega=entrega,
                                    producto=producto,
                                    cantidad=producto_grupo.cantidad
                                )
                                productos_entregados.append(detalle)

                            except Producto.DoesNotExist:
                                productos_sin_stock.append(f"Sin producto: {producto_grupo.categoria.nombre} - Talla: {talla}")
                            except InventarioBodega.DoesNotExist:
                                productos_sin_stock.append(f"Sin stock: {producto_grupo.categoria.nombre} - Talla: {talla}")
                                
                               
                        
                        print("Tipo de usuario recibido: linea 963", type(request.user))
                        if productos_entregados:
                            print("Tipo de usuario recibido:linea 965", type(request.user))
                            generar_salida_por_entrega(entrega, productos_entregados, request.user)
                            entregas += 1

                        if productos_sin_stock:
                            empleados_sin_entrega.append(
                                f"{empleado.nombre} ({cedula}) - Sin stock para: {', '.join(productos_sin_stock)}"
                            )

                    else:
                        errores = []
                        if not GrupoDotacion.objects.filter(cargos=cargo).exists():
                            errores.append(f"Cargo: '{cargo.nombre}'")
                        if not GrupoDotacion.objects.filter(cliente=cliente).exists():
                            errores.append(f"Cliente: '{cliente.nombre}'")
                        if not GrupoDotacion.objects.filter(ciudades=ciudad).exists():
                            errores.append(f"Ciudad: '{ciudad.nombre}'")
                        if not GrupoDotacion.objects.filter(genero=genero).exists():
                            errores.append(f"Genero: '{genero}'")

                        motivo = ', '.join(errores)
                        empleados_sin_entrega.append(
                            f"{empleado.nombre} ({cedula}) - Sin grupo para: {motivo}"
                        )

                if contador > 0:
                    mensaje = f"✅ Se cargaron {contador} empleados y se generaron {entregas} entregas."
                    if empleados_sin_entrega:
                        mensaje += f" ⚠️ Sin entrega para {len(empleados_sin_entrega)} empleados."
                        request.session['empleados_sin_entrega'] = empleados_sin_entrega
                    messages.success(request, mensaje)
                else:
                    messages.warning(request, "⚠️ No se cargó ningún empleado nuevo.")

                return redirect('cargar_empleados')

            except Exception as e:
                print("Tipo del objeto recibido como usuario: linea 1002", type(request))
               
                messages.error(request, f"❌ Error al procesar el archivo: {str(e)}")
    else:
        form = CargarArchivoForm()

    empleados_sin_entrega = request.session.pop('empleados_sin_entrega', [])

    return render(request, 'cargar_empleados.html', {
        'form': form,
        'empleados_sin_entrega': empleados_sin_entrega
    })

# Comentado era el codigo que servia

# def cargar_empleados_desde_excel(request):
#     if request.method == 'POST':
#         form = CargarArchivoForm(request.POST, request.FILES)
#         if form.is_valid():
#             archivo = request.FILES['archivo']
#             try:
#                 df = pd.read_excel(archivo)
#                 df.columns = df.columns.str.strip()

#                 try:
#                     df.columns.values[8] = 'CANTIDAD_CAMISA'
#                     df.columns.values[10] = 'CANTIDAD_PANTALON'
#                     df.columns.values[12] = 'CANTIDAD_ZAPATOS'
#                 except IndexError:
#                     messages.error(request, "❌ El archivo no tiene suficientes columnas.")
#                     return render(request, 'cargar_empleados.html', {'form': form})

#                 df.rename(columns={
#                     'NUMERO DE DO CUMENTO': 'NUMERO DE DOCUMENTO',
#                     'CANTIDAD ': 'CANTIDAD_CAMISA',
#                     'CANTIDAD': 'CANTIDAD_PANTALON',
#                     'Unnamed: 0': 'IGNORAR_1',
#                     'Unnamed: 15': 'IGNORAR_2',
#                     'Unnamed: 21': 'IGNORAR_3',
#                     '   SUCURSAL': 'SUCURSAL'
#                 }, inplace=True)

#                 columnas_requeridas = [
#                     'NUMERO DE DOCUMENTO', 'NOMBRE COMPLETO', 'CENTRO TRABAJO', 'INGRESO', 'CARGO',
#                     'CLIENTE', 'C. COSTO', 'SEXO', 'TALLA CAMISA', 'CANTIDAD_CAMISA',
#                     'TALLA PANTALON', 'CANTIDAD_PANTALON', 'TALLA ZAPATOS',
#                     'CANTIDAD_ZAPATOS', 'BOTA CAUCHO'
#                 ]
#                 faltantes = [col for col in columnas_requeridas if col not in df.columns]
#                 if faltantes:
#                     messages.error(request, f"❌ Faltan columnas en el archivo: {faltantes}")
#                     return render(request, 'cargar_empleados.html', {'form': form})

#                 contador, entregas = 0, 0
#                 empleados_sin_entrega = []

#                 try:
#                     bodega_dotacion = Bodega.objects.get(nombre__iexact="Principal")
#                 except Bodega.DoesNotExist:
#                     messages.error(request, "❌ No se encontró la bodega 'Principal'.")
#                     return render(request, 'cargar_empleados.html', {'form': form})

#                 for _, fila in df.iterrows():
#                     cedula = safe_str(fila['NUMERO DE DOCUMENTO']).strip()
#                     if EmpleadoDotacion.objects.filter(cedula=cedula).exists():
#                         continue

#                     cliente, _ = Cliente.objects.get_or_create(nombre=safe_str(fila['CLIENTE']).strip())
#                     ciudad, _ = Ciudad.objects.get_or_create(nombre=safe_str(fila['CENTRO TRABAJO']).strip().title())
#                     cargo, _ = Cargo.objects.get_or_create(nombre=safe_str(fila['CARGO']).strip())
#                     centro_costo = safe_str(fila['C. COSTO']).strip()

#                     empleado = EmpleadoDotacion.objects.create(
#                         cedula=cedula,
#                         nombre=safe_str(fila['NOMBRE COMPLETO']),
#                         ciudad=ciudad,
#                         fecha_ingreso=pd.to_datetime(fila['INGRESO'], errors='coerce'),
#                         cargo=cargo,
#                         cliente=cliente,
#                         centro_costo=centro_costo,
#                         sexo=safe_str(fila['SEXO']).upper(),
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
#                         cargos__nombre__iexact=empleado.cargo,
#                         ciudades__nombre__iexact=empleado.ciudad,
#                         cliente__nombre__icontains=empleado.cliente,
#                         genero__iexact=empleado.sexo
#                     ).distinct()

#                     genero = safe_str(fila['SEXO']).upper()

#                     if grupos.exists():
#                         grupo = grupos.first()
#                         productos = GrupoDotacionProducto.objects.filter(grupo=grupo)

#                         # Validación de stock
#                         productos_sin_stock = []
#                         for producto_grupo in productos:
#                             try:
#                                 inventario = InventarioBodega.objects.get(
#                                     bodega=bodega_dotacion,
#                                     producto=producto_grupo.producto
#                                 )
#                                 if inventario.stock < producto_grupo.cantidad:
#                                     productos_sin_stock.append(producto_grupo.producto.nombre)
#                             except InventarioBodega.DoesNotExist:
#                                 productos_sin_stock.append(producto_grupo.producto.nombre)

#                         if productos_sin_stock:
#                             empleados_sin_entrega.append(
#                                 f"{empleado.nombre} ({cedula}) - Sin stock para productos: {', '.join(productos_sin_stock)}"
#                             )
#                             continue

#                         # Generar entrega
#                         entrega = EntregaDotacion.objects.create(empleado=empleado, grupo=grupo)

#                         productos_entregados = []
#                         for producto_grupo in productos:
#                             detalle = DetalleEntregaDotacion.objects.create(
#                                 entrega=entrega,
#                                 producto=producto_grupo.producto,
#                                 cantidad=producto_grupo.cantidad
#                             )
#                             productos_entregados.append(detalle)

#                         generar_salida_por_entrega(entrega, productos_entregados, request.user)
#                         entregas += 1
#                     else:
#                         errores = []
#                         if not GrupoDotacion.objects.filter(cargos=cargo).exists():
#                             errores.append(f"Cargo: '{cargo.nombre}'")
#                         if not GrupoDotacion.objects.filter(cliente=cliente).exists():
#                             errores.append(f"Cliente: '{cliente.nombre}'")
#                         if not GrupoDotacion.objects.filter(ciudades=ciudad).exists():
#                             errores.append(f"Ciudad: '{ciudad.nombre}'")
#                         if not GrupoDotacion.objects.filter(genero=genero).exists():
#                             errores.append(f"Género: '{genero}'")

#                         motivo = ', '.join(errores)
#                         empleados_sin_entrega.append(
#                             f"{empleado.nombre} ({cedula}) - Sin grupo para {motivo}"
#                         )

#                 if contador > 0:
#                     mensaje = f"✅ Se cargaron {contador} empleados y se generaron {entregas} entregas."
#                     if empleados_sin_entrega:
#                         mensaje += f" ⚠️ No se generó entrega para {len(empleados_sin_entrega)} empleados."
#                         request.session['empleados_sin_entrega'] = empleados_sin_entrega
#                     messages.success(request, mensaje)
#                 else:
#                     messages.warning(request, "⚠️ No se cargó ningún empleado nuevo.")

#                 return redirect('cargar_empleados')

#             except Exception as e:
#                 messages.error(request, f"❌ Error al procesar el archivo: {str(e)}")

#     else:
#         form = CargarArchivoForm()

#     empleados_sin_entrega = request.session.pop('empleados_sin_entrega', [])

#     return render(request, 'cargar_empleados.html', {
#         'form': form,
#         'empleados_sin_entrega': empleados_sin_entrega
#     })




def descargar_pdf_entrega(request, entrega_id):
    entrega = get_object_or_404(EntregaDotacion, pk=entrega_id)
    return generar_formato_entrega_pdf(entrega)

