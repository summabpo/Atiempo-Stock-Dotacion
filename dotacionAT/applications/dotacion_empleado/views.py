
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

import pandas as pd
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from .forms import CargarArchivoForm
from .models import EmpleadoDotacion
from django.contrib.auth.decorators import login_required


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


def cargar_empleados_desde_excel(request):
    if request.method == 'POST':
        form = CargarArchivoForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo']
            try:
                df = pd.read_excel(archivo)
                
                df.columns = df.columns.str.strip()  # Elimina espacios o saltos de línea
                
                df = pd.read_excel(archivo)
                df.columns = df.columns.str.strip()  # Limpia espacios

                # Asignar nombres únicos a columnas duplicadas
                df.columns.values[8] = 'CANTIDAD_CAMISA'
                df.columns.values[10] = 'CANTIDAD_PANTALON'
                df.columns.values[12] = 'CANTIDAD_ZAPATOS'

                # Renombrar columnas sucias o incorrectas
                df.rename(columns={
                                'NUMERO DE DO CUMENTO': 'NUMERO DE DOCUMENTO',
                                'CANTIDAD ': 'CANTIDAD_CAMISA',         # Aquí estaba la cantidad de camisa
                                'CANTIDAD': 'CANTIDAD_PANTALON',      # Aquí está la cantidad de pantalón
                                'CANTIDAD': 'CANTIDAD_ZAPATOS',
                                'Unnamed: 0': 'IGNORAR_1',
                                'Unnamed: 15': 'IGNORAR_2',
                                'Unnamed: 21': 'IGNORAR_3',
                                '   SUCURSAL': 'SUCURSAL'
                            }, inplace=True)

                print("🧪 Columnas detectadas:", df.columns.tolist())
                print(df.head())  # Mostrar primeras filas para validar

                columnas_necesarias = [
                    'IGNORAR_1', 'NOMBRE COMPLETO', 'SUCURSAL', 'INGRESO', 'CARGO', 'CLIENTE',
                    'C. COSTO', 'SEXO', 'TALLA CAMISA', 'CANTIDAD_CAMISA',
                    'TALLA PANTALON', 'CANTIDAD_PANTALON',
                    'TALLA ZAPATOS', 'CANTIDAD_ZAPATOS', 'BOTA CAUCHO'
                ]

                faltantes = [col for col in columnas_necesarias if col not in df.columns]
                if faltantes:
                    messages.error(request, f"❌ Faltan columnas en el archivo: {faltantes}")
                    return render(request, 'cargar_empleados.html', {'form': form})

                contador = 0
                for _, fila in df.iterrows():
                    cedula = safe_str(fila['NUMERO DE DOCUMENTO'])

                    if EmpleadoDotacion.objects.filter(cedula=cedula).exists():
                        continue  # Evitar duplicados

                    EmpleadoDotacion.objects.create(
                        cedula=cedula,
                        nombre=safe_str(fila['NOMBRE COMPLETO']),
                        ciudad=safe_str(fila['SUCURSAL']),
                        fecha_ingreso=pd.to_datetime(fila['INGRESO'], errors='coerce'),
                        cargo=safe_str(fila['CARGO']),
                        cliente=safe_str(fila['CLIENTE']),
                        centro_costo=safe_str(fila['C. COSTO']),
                        sexo=safe_str(fila['SEXO']),
                        talla_camisa=safe_str(fila['TALLA CAMISA']),
                        cantidad_camisa=safe_int(fila['CANTIDAD_CAMISA']),
                        talla_pantalon=safe_str(fila['TALLA PANTALON']),
                        cantidad_pantalon=safe_int(fila['CANTIDAD_PANTALON']),
                        talla_zapatos=safe_str(fila['TALLA ZAPATOS']),
                        cantidad_zapatos=safe_int(fila['CANTIDAD_ZAPATOS']),
                        cantidad_botas_caucho=safe_int(fila['BOTA CAUCHO']),
                    )
                    contador += 1

                if contador > 0:
                    messages.success(request, f"✅ Se cargaron {contador} empleados correctamente.")
                else:
                    messages.warning(request, "⚠️ No se cargó ningún empleado. Puede que ya existan.")

                return redirect('cargar_empleados')
            except Exception as e:
                messages.error(request, f"❌ Error al procesar el archivo: {e}")
    else:
        form = CargarArchivoForm()

    return render(request, 'cargar_empleados.html', {'form': form})