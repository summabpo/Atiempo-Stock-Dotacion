import threading
from applications.inventario.models import  InventarioBodega
from django.utils import timezone
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse, JsonResponse, FileResponse
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
from .utils import safe_str, safe_int, generar_formato_entrega_pdf, limpiar_dataframe, obtener_o_crear_empleado, crear_entrega_dotacion
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
from django.db.models import Count, Sum
from applications.dotacion_empleado.utils import generar_pdf_entregas
from urllib.parse import unquote
from django.db.models import F, Func, Value
from django.db.models.functions import Replace, Upper
from django.db.models import CharField, Value
from django.db.models.functions import Concat
from django.template.loader import render_to_string
import pdfkit  # o WeasyPrint, xhtml2pdf, etc.
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
import os
from django.conf import settings
from reportlab.platypus import Image
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache



def get_or_none(modelo, **filtros):
    try:
        return modelo.objects.get(**filtros)
    except modelo.DoesNotExist:
        return None

@login_required
def historial_entregas(request):
    periodo = request.GET.get('periodo', '')
    cliente = request.GET.get('cliente', '').strip()

    entregas = EntregaDotacion.objects.select_related('empleado', 'grupo') \
        .prefetch_related('detalles__producto')

    if periodo:
        try:
            mes, anio = periodo.split('/')
            entregas = entregas.filter(fecha_entrega__month=int(mes), fecha_entrega__year=int(anio))
        except ValueError:
            pass

    if cliente:
        entregas = entregas.filter(empleado__cliente__icontains=cliente)

    entregas = entregas.order_by('-fecha_entrega')

    return render(request, 'historial_entregas.html', {
        'entregas': entregas,
        'periodo': periodo,
        'cliente': cliente
    })
    
    
    
def historial_entregas2(request):
    entregas = EntregaDotacion.objects.select_related('empleado', 'grupo') \
        .order_by('-fecha_entrega')
    return render(request, 'historial_entregas2.html', {'entregas': entregas})


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
                'ciudad': c.ciudad.nombre,
                'cargo': c.cargo.nombre,
                'cliente': c.cliente.nombre,
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



@login_required
def historial_entregas(request):
    entregas = EntregaDotacion.objects.select_related('empleado', 'grupo').order_by('-fecha_entrega')
    return render(request, 'historial_entregas.html', {'entregas': entregas})



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
    

# Variable global para progreso (luego la puedes llevar a cache si quieres)
PROGRESO_CARGA = {"total": 0, "actual": 0}
    

# def cargar_empleados_desde_excel(request):
#     empleados_sin_entrega = []
#     global PROGRESO_CARGA
    
#     if request.method == 'POST':
#         set_current_user(request.user)
#         form = CargarArchivoForm(request.POST, request.FILES)

#         if form.is_valid():
#             archivo = request.FILES['archivo']
#             print("📂 Archivo recibido:", archivo.name)
#             periodo = form.cleaned_data['periodo']
#             tipo_entrega = form.cleaned_data['tipo_entrega']
#             print("📅 Periodo recibido:", periodo)

#             try:
#                 # 🔹 1. Leemos el archivo Excel
#                 df = pd.read_excel(archivo)

#                 # reiniciamos progreso en cache
#                 total = len(df)
#                 cache.set('progreso_carga', {"total": total, "actual": 0}, timeout=600)
                
                
#                 print("Antes de limpiar:")
#                 print(df.head())

#                 # 🔹 2. Aplicamos el helper de limpieza
#                 df = limpiar_dataframe(df)
                
#                 print("Después de limpiar:")
#                 print(df.head())


#                 # 🔹 3. Validamos que venga la columna de documento (para evitar errores posteriores)
#                 if "NUMERO_DE_DOCUMENTO" not in df.columns:
#                     messages.error(request, "❌ El archivo no contiene la columna 'NUMERO DE DOCUMENTO'.")
#                     return render(request, 'cargar_empleados.html', {'form': form})

#                 # 🔹 4. Eliminamos filas sin documento
#                 df = df.dropna(subset=['NUMERO_DE_DOCUMENTO'])
#                 df = df[df['NUMERO_DE_DOCUMENTO'].astype(str).str.strip() != '']

#                 # 🔹 5. Normalizamos columnas que quieras renombrar
#                 df.rename(columns={
#                     'NUMERO DE DO CUMENTO': 'NUMERO_DE_DOCUMENTO',
#                     'Unnamed: 0': 'IGNORAR_1',
#                     'Unnamed: 15': 'IGNORAR_2',
#                     'Unnamed: 21': 'IGNORAR_3',
#                     ' SUCURSAL': 'SUCURSAL'
#                 }, inplace=True)

#                 # 🔹 6. Validamos columnas requeridas
#                 columnas_requeridas = [
#                     'NUMERO_DE_DOCUMENTO',
#                     'NOMBRE_COMPLETO',
#                     'CENTRO_TRABAJO',
#                     'INGRESO',
#                     'CARGO',
#                     'CLIENTE',
#                     'C._COSTO',
#                     'SEXO',
#                     'TALLA_CAMISA',
#                     'TALLA_PANTALON',
#                     'TALLA_ZAPATOS'
#                 ]
#                 faltantes = [col for col in columnas_requeridas if col not in df.columns]
#                 if faltantes:
#                     messages.error(request, f"❌ Faltan columnas en el archivo: {faltantes}")
#                     return render(request, 'cargar_empleados.html', {'form': form})

#                 contador, entregas = 0, 0

#                 try:
#                     bodega_dotacion = Bodega.objects.get(nombre__iexact="Principal")
#                 except Bodega.DoesNotExist:
#                     messages.error(request, "❌ No se encontró la bodega 'Principal'.")
#                     return render(request, 'cargar_empleados.html', {'form': form})

#                 # 🔹 7. Procesamos cada fila del DataFrame
#                 for _, fila in df.iterrows():
#                     cedula = safe_str(fila['NUMERO_DE_DOCUMENTO']).strip()
#                     print("\n🆕 Procesando fila:", cedula)

#                     if EmpleadoDotacion.objects.filter(cedula=cedula).exists():
#                         progreso = cache.get('progreso_carga', {"total": total, "actual": 0})
#                         progreso["actual"] += 1
#                         cache.set('progreso_carga', progreso, timeout=600)
#                         continue
                    
#                     empleado = obtener_o_crear_empleado(fila)

#                     cliente, _ = Cliente.objects.get_or_create(nombre=safe_str(fila['CLIENTE']).strip())
#                     ciudad, _ = Ciudad.objects.get_or_create(nombre=safe_str(fila['CENTRO_TRABAJO']).strip().title())
#                     cargo, _ = Cargo.objects.get_or_create(nombre=safe_str(fila['CARGO']).strip())
#                     centro_costo = safe_str(fila['C._COSTO']).strip()

#                     # fecha_ingreso = pd.to_datetime(fila['INGRESO'], errors='coerce')
#                     # if pd.isna(fecha_ingreso):
#                     #     fecha_ingreso = None
#                     # else:
#                     #     fecha_ingreso = fecha_ingreso.date()

#                     # talla_camisa = normalizar_talla(fila['TALLA_CAMISA'], categoria="CAMISA")
#                     # talla_pantalon = normalizar_talla(fila['TALLA_PANTALON'], categoria="PANTALON")
#                     # talla_zapatos = normalizar_talla(fila['TALLA_ZAPATOS'], categoria="BOTAS")

#                     # empleado = EmpleadoDotacion.objects.create(
#                     #     cedula=safe_str_number(fila['NUMERO_DE_DOCUMENTO']),
#                     #     nombre=safe_str(fila['NOMBRE_COMPLETO']),
#                     #     ciudad=safe_str(fila['CENTRO_TRABAJO']),  # Texto directo
#                     #     fecha_ingreso=fecha_ingreso,
#                     #     cargo=safe_str(fila['CARGO']),
#                     #     cliente=safe_str(fila['CLIENTE']),  # Texto directo
#                     #     centro_costo=safe_str(fila['C._COSTO']),
#                     #     sexo=safe_str(fila['SEXO']),
#                     #     talla_camisa=talla_camisa,
#                     #     cantidad_camisa=int(fila.get('CANTIDAD_CAMISA', 0) or 0),
#                     #     talla_pantalon=talla_pantalon,
#                     #     cantidad_pantalon=int(fila.get('CANTIDAD_PANTALON', 0) or 0),
#                     #     talla_zapatos=talla_zapatos,
#                     #     cantidad_zapatos=int(fila.get('CANTIDAD_ZAPATOS', 0) or 0),
#                     #     cantidad_botas_caucho=int(fila.get('BOTAS_CAUCHO', 0) or 0),
#                     # )
#                     contador += 1

#                     # 🔹 cada fila que procesas → actualizas progreso
#                     progreso = cache.get('progreso_carga', {"total": total, "actual": 0})
#                     progreso["actual"] += 1
#                     cache.set('progreso_carga', progreso, timeout=600)

#                     cargo_obj = Cargo.objects.get(nombre__iexact=empleado.cargo)
#                     grupos = GrupoDotacion.objects.filter(
#                         cargos=cargo_obj,
#                         ciudades__nombre__iexact=empleado.ciudad,
#                         cliente__nombre__icontains=empleado.cliente,
#                         genero__iexact=empleado.sexo
#                     ).distinct()

#                     genero = safe_str(fila['SEXO']).upper()

#                     if grupos.exists():
#                         grupo = grupos.first()
#                         productos = GrupoDotacionProducto.objects.filter(grupo=grupo)

#                         productos_sin_stock = []
#                         productos_entregados = []

#                         for producto_grupo in productos:
#                             talla = obtener_talla_para_categoria(producto_grupo.categoria, empleado)
#                             try:
#                                 producto = Producto.objects.get(
#                                     nombre__icontains=talla,
#                                     categoria=producto_grupo.categoria
#                                 )
#                                 inventario = InventarioBodega.objects.get(
#                                     bodega=bodega_dotacion,
#                                     producto=producto
#                                 )

#                                 if inventario.stock < producto_grupo.cantidad:
#                                     productos_sin_stock.append(producto.nombre)
#                                     continue

#                                 entrega = EntregaDotacion.objects.get_or_create(
#                                     empleado=empleado,
#                                     grupo=grupo,
#                                     tipo_entrega=tipo_entrega,
#                                     periodo= periodo 
#                                 )[0]

#                                 detalle = DetalleEntregaDotacion.objects.create(
#                                     entrega=entrega,
#                                     producto=producto,
#                                     cantidad=producto_grupo.cantidad
#                                 )
#                                 productos_entregados.append(detalle)

#                             except Producto.DoesNotExist:
#                                 productos_sin_stock.append(
#                                     f"Sin producto: {producto_grupo.categoria.nombre} - Talla: {talla}"
#                                 )
#                             except InventarioBodega.DoesNotExist:
#                                 productos_sin_stock.append(
#                                     f"Sin stock: {producto_grupo.categoria.nombre} - Talla: {talla}"
#                                 )

#                         print("Tipo de usuario recibido: linea 963", type(request.user))

#                         if productos_entregados:
#                             print("Tipo de usuario recibido: linea 965", type(request.user))
#                             generar_salida_por_entrega(entrega, productos_entregados, request.user)
#                             entregas += 1

#                         if productos_sin_stock:
#                             empleados_sin_entrega.append(
#                                 f"{empleado.nombre} ({cedula}) - Sin stock para: {', '.join(productos_sin_stock)}"
#                             )

#                     else:
#                         errores = []
#                         if not GrupoDotacion.objects.filter(cargos=cargo).exists():
#                             errores.append(f"Cargo: '{cargo.nombre}'")
#                         if not GrupoDotacion.objects.filter(cliente=cliente).exists():
#                             errores.append(f"Cliente: '{cliente.nombre}'")
#                         if not GrupoDotacion.objects.filter(ciudades=ciudad).exists():
#                             errores.append(f"Ciudad: '{ciudad.nombre}'")
#                         if not GrupoDotacion.objects.filter(genero=genero).exists():
#                             errores.append(f"Genero: '{genero}'")

#                         motivo = ', '.join(errores)
#                         empleados_sin_entrega.append(
#                             f"{empleado.nombre} ({cedula}) - Sin grupo para: {motivo}"
#                         )
                        
#                     # 🔹 actualizamos progreso
#                     PROGRESO_CARGA["actual"] += 1
                        
#                 if contador > 0:
#                     mensaje = f"✅ Se cargaron {contador} empleados y se generaron {entregas} entregas."
#                     if empleados_sin_entrega:
#                         mensaje += f" ⚠️ Sin entrega para {len(empleados_sin_entrega)} empleados."
#                     request.session['empleados_sin_entrega'] = empleados_sin_entrega
#                     messages.success(request, mensaje)
#                 else:
#                     messages.warning(request, "⚠️ No se cargó ningún empleado nuevo.")

#                 return redirect('cargar_empleados')

#             except Exception as e:
#                 print("Tipo del objeto recibido como usuario: linea 1002", type(request))
#                 messages.error(request, f"❌ Error al procesar el archivo: {str(e)}")

#     else:
#         form = CargarArchivoForm()
#         empleados_sin_entrega = request.session.pop('empleados_sin_entrega', [])

#     return render(request, 'cargar_empleados.html', {
#         'form': form,
#         'empleados_sin_entrega': empleados_sin_entrega
#     })

## este codigo era el que estaba







def cargar_empleados_desde_excel(request):
    empleados_sin_entrega = []
    global PROGRESO_CARGA
    advertencias = []

    total_filas = 0
    entregas_creadas = 0
    sin_stock = []
    ya_tenia_ingreso = []
    no_cumple_ley = []
    sin_grupo = []

    if request.method == 'POST':
        set_current_user(request.user)
        form = CargarArchivoForm(request.POST, request.FILES)

        if form.is_valid():
            archivo = request.FILES['archivo']
            periodo = form.cleaned_data['periodo']
            tipo_entrega = form.cleaned_data['tipo_entrega']
            print(tipo_entrega)

            try:
                # 🔹 1. Leemos el archivo Excel
                df = pd.read_excel(archivo)

                # reiniciamos progreso en cache
                total = len(df)
                cache.set('progreso_carga', {"total": total, "actual": 0}, timeout=600)

                # 🔹 2. Aplicamos limpieza
                df = limpiar_dataframe(df)

                # 🔹 3. Validaciones básicas
                if "NUMERO_DE_DOCUMENTO" not in df.columns:
                    messages.error(request, "❌ El archivo no contiene la columna 'NUMERO DE DOCUMENTO'.")
                    return render(request, 'cargar_empleados.html', {'form': form})

                df = df.dropna(subset=['NUMERO_DE_DOCUMENTO'])
                df = df[df['NUMERO_DE_DOCUMENTO'].astype(str).str.strip() != '']

                columnas_requeridas = [
                    'NUMERO_DE_DOCUMENTO', 'NOMBRE_COMPLETO', 'CENTRO_TRABAJO',
                    'INGRESO', 'CARGO', 'CLIENTE', 'C._COSTO',
                    'SEXO', 'TALLA_CAMISA', 'TALLA_PANTALON', 'TALLA_ZAPATOS'
                ]
                faltantes = [col for col in columnas_requeridas if col not in df.columns]
                if faltantes:
                    messages.error(request, f"❌ Faltan columnas en el archivo: {faltantes}")
                    return render(request, 'cargar_empleados.html', {'form': form})

                contador, entregas = 0, 0

                try:
                    bodega_dotacion = Bodega.objects.get(nombre__iexact="Principal")
                except Bodega.DoesNotExist:
                    messages.error(request, "❌ No se encontró la bodega 'Principal'.")
                    return render(request, 'cargar_empleados.html', {'form': form})

                # 🔹 4. Procesamos cada fila
                for _, fila in df.iterrows():
                    cedula = safe_str(fila['NUMERO_DE_DOCUMENTO']).strip()
                    total_filas += 1

                    empleado = obtener_o_crear_empleado(fila)
                    if not empleado:
                        advertencias.append(f"Cédula {cedula}: no se creó/obtuvo empleado.")
                        progreso = cache.get('progreso_carga', {"total": total, "actual": 0})
                        progreso["actual"] += 1
                        cache.set('progreso_carga', progreso, timeout=600)
                        continue

                    contador += 1
                    progreso = cache.get('progreso_carga', {"total": total, "actual": 0})
                    progreso["actual"] += 1
                    cache.set('progreso_carga', progreso, timeout=600)

                    cargo_obj = empleado.cargo
                    grupos = GrupoDotacion.objects.filter(
                        cargos=cargo_obj,
                        ciudades__nombre__iexact=empleado.ciudad.nombre if empleado.ciudad else None,
                        cliente=empleado.cliente,
                        genero__iexact=empleado.sexo
                    ).distinct()

                    if not grupos.exists():
                        empleados_sin_entrega.append(f"{empleado.nombre} ({cedula}) - Sin grupo de dotación")
                        sin_grupo.append(f"{empleado.nombre} ({cedula}) - Sin grupo de dotación")
                        continue

                    grupo = grupos.first()
                    productos = GrupoDotacionProducto.objects.filter(grupo=grupo)

                    entrega = crear_entrega_dotacion(empleado, grupo, tipo_entrega, periodo)
                    if not entrega:
                        motivo = f"No cumple reglas para entrega {tipo_entrega.lower()}"
                        no_cumple_ley.append(f"{empleado.nombre} ({cedula}) - {motivo}")
                        advertencias.append(f"{empleado.nombre} ({empleado.cedula}) - {motivo}")
                        empleados_sin_entrega.append(f"{empleado.nombre} ({cedula}) - {motivo}")
                        continue

                    productos_sin_stock = []
                    productos_entregados = []

                    for producto_grupo in productos:
                        talla = obtener_talla_para_categoria(producto_grupo.categoria, empleado)
                        try:
                            producto = Producto.objects.get(
                                nombre__icontains=talla,
                                categoria=producto_grupo.categoria
                            )
                            inventario = InventarioBodega.objects.get(
                                bodega=bodega_dotacion,
                                producto=producto
                            )

                            if inventario.stock < producto_grupo.cantidad:
                                productos_sin_stock.append(f"{producto.nombre} - requerido {producto_grupo.cantidad}")
                                continue

                            detalle = DetalleEntregaDotacion.objects.create(
                                entrega=entrega,
                                producto=producto,
                                cantidad=producto_grupo.cantidad
                            )
                            productos_entregados.append(detalle)

                        except Producto.DoesNotExist:
                            productos_sin_stock.append(
                                f"Sin producto: {producto_grupo.categoria.nombre} - Talla: {talla}"
                            )
                        except InventarioBodega.DoesNotExist:
                            productos_sin_stock.append(
                                f"Sin stock: {producto_grupo.categoria.nombre} - Talla: {talla}"
                            )

                    if not productos_entregados:
                        try:
                            entrega.delete()
                        except Exception:
                            pass
                        empleados_sin_entrega.append(
                            f"{empleado.nombre} ({cedula} {motivo}) "
                        )
                        sin_stock.append(f"{empleado.nombre} ({cedula} {motivo}) - Sin stock total")
                        continue

                    generar_salida_por_entrega(entrega, productos_entregados, request.user)
                    entregas += 1

                    if productos_sin_stock:
                        motivo = f"Sin stock para: {', '.join(productos_sin_stock)}"
                        empleados_sin_entrega.append(f"{empleado.nombre} ({cedula}) - {motivo}")

                # --- Mensaje resumen y detalles en plantilla ---
                if contador > 0:
                    resumen = f"✅ Se procesaron {contador} filas y se generaron {entregas} entregas."
                    messages.success(request, resumen)

                    # Construir lista de detalles
                    empleados_detalle = []
                    for e in empleados_sin_entrega:
                        # separa el motivo si existe
                        nombre_cedula, sep, motivo = e.rpartition(" - ")
                        # extraer nombre y cédula
                        nombre = nombre_cedula.split("(")[0].strip()
                        cedula = nombre_cedula[nombre_cedula.find("(")+1 : nombre_cedula.find(")")]
                        empleados_detalle.append({
                            "nombre": nombre,
                            "cedula": cedula,
                            "motivo": motivo if motivo else "No especificado"
                        })

                    return render(request, "cargar_empleados_resultado.html", {
                        "mensaje": resumen,
                        "empleados_sin_entrega": empleados_detalle
                    })

                else:
                    messages.warning(request, "⚠️ No se procesó ninguna fila válida.")
                    return redirect("cargar_empleados")

            except Exception as e:
                messages.error(request, f"❌ Error al procesar el archivo: {str(e)}")
                return redirect("cargar_empleados")

    else:
        form = CargarArchivoForm()

    return render(request, 'cargar_empleados.html', {
        'form': form,
    })




def progreso_carga(request):
    progreso = cache.get('progreso_carga', {"total": 1, "actual": 0})
    porcentaje = int((progreso["actual"] / progreso["total"]) * 100) if progreso["total"] > 0 else 0
    return JsonResponse({"progreso": porcentaje})

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


def vista_consolidado(request):
    consolidado = (
        EntregaDotacion.objects
        .values(
            'empleado__cliente__nombre',  # nombre directo
            'periodo',
            'tipo_entrega'
        )
        .annotate(total_entregas=Count('id'))
        .order_by('empleado__cliente__nombre', 'periodo')
    )
    return render(request, 'consolidado.html', {'consolidado': consolidado})



# Función para reemplazar caracteres en DB
class Replace(Func):
    function = 'REPLACE'
    arity = 3

def generar_pdf_por_periodo(request):
    # Obtener periodo del query string (ejemplo: ?periodo=08/2025)
    periodo = request.GET.get('periodo')
    if not periodo:
        return HttpResponse("Debe especificar un periodo.", status=400)

    try:
        mes, anio = map(int, periodo.split('/'))
    except ValueError:
        return HttpResponse("Formato de periodo incorrecto. Use MM/YYYY.", status=400)

    # Filtrar entregas por periodo
    entregas = EntregaDotacion.objects.select_related('empleado', 'grupo') \
        .prefetch_related('detalles__producto') \
        .filter(fecha_entrega__month=mes, fecha_entrega__year=anio)

    if not entregas.exists():
        return HttpResponse("No hay entregas para este periodo.", status=404)

    # Aquí tu código existente para generar PDF...
    buffer = generar_pdf_entregas(entregas)
    return FileResponse(buffer, as_attachment=True, filename=f'entregas_{periodo}.pdf')


def generar_pdf_por_entrega(request, entrega_id):
    entrega = get_object_or_404(
        EntregaDotacion.objects.select_related('empleado', 'grupo').prefetch_related('detalles__producto'),
        id=entrega_id
    )
    empleado = entrega.empleado

    ruta_logo = os.path.join(settings.BASE_DIR, 'applications', 'ciudades', 'static', 'index', 'img', 'logoAtiempo.png')
    logo = Image(ruta_logo, width=80, height=40) if os.path.exists(ruta_logo) else ''

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    styles = getSampleStyleSheet()

    # --- Estilos personalizados ---
    parrafo_estilo = ParagraphStyle(
        name="TablaWrap",
        fontSize=9,
        leading=10,
        wordWrap='CJK',
        alignment=1,
        fontName='Helvetica-Bold'
    )

    # --- Encabezado ---
    encabezado_data = [
        ['Código: FOR-GC-007', Paragraph('FORMATO DE ENTREGA ELEMENTOS DE TRABAJO', parrafo_estilo), logo],
        ['Versión: 02', '', ''],
        ['Fecha vigencia: 02/04/2019', '', '']
    ]
    encabezado_table = Table(encabezado_data, colWidths=[4.8*cm, 8.7*cm, 3.5*cm])
    encabezado_table.setStyle(TableStyle([
        ('SPAN', (1, 0), (1, 2)),
        ('SPAN', (2, 0), (2, 2)),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
    ]))
    elements.append(encabezado_table)
    elements.append(Spacer(1, 0.5 * cm))

    # === Datos del trabajador ===
    datos_trabajador = [
        ['Nombre Trabajador', Paragraph(empleado.nombre, styles['Normal']), 'N.° ID', str(empleado.cedula)],
        ['Empresa', Paragraph(str(empleado.cliente), styles['Normal']), 'Cargo', Paragraph(str(empleado.cargo), styles['Normal'])],
        ['Fecha Ingreso',
         empleado.fecha_ingreso.strftime("%d/%m/%Y") if empleado.fecha_ingreso else '',
         'Fecha de entrega',
         f"{entrega.fecha_entrega.strftime('%m/%Y')}  |  Periodo: {entrega.periodo}"]
    ]
    tabla_datos = Table(datos_trabajador, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
    tabla_datos.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elements.append(tabla_datos)
    elements.append(Spacer(1, 0.5 * cm))

    # === Checkboxes ===
    checkbox_texto = Paragraph("Se hace entrega de los siguientes elementos de trabajo:", styles['Normal'])
    checkboxes_data = [
        [checkbox_texto, '', '', ''],
        ['[X] DOTACIÓN', '[ ] EPP', '[ ] HERRAMIENTAS', '[ ] OTROS']
    ]
    tabla_checkbox = Table(checkboxes_data, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
    tabla_checkbox.setStyle(TableStyle([
        ('SPAN', (0, 0), (3, 0)),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elements.append(tabla_checkbox)
    elements.append(Spacer(1, 0.5 * cm))

    # === Tabla artículos ===
    tabla_data = [['ARTÍCULO', 'CANTIDAD']]
    for detalle in entrega.detalles.all():
        tabla_data.append([detalle.producto.nombre, str(detalle.cantidad)])
    tabla = Table(tabla_data, colWidths=[12*cm, 5*cm])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.8, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    elements.append(tabla)
    elements.append(Spacer(1, 0.5 * cm))

    # === Observaciones ===
    observacion = entrega.observaciones or " "
    observacion_table = Table([
        [Paragraph("<b>OBSERVACIONES:</b>", styles['Normal'])],
        [Paragraph(observacion, styles['Normal'])]
    ], colWidths=[17*cm])
    observacion_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('TOPPADDING', (0, 1), (0, 1), 20),
        ('BOTTOMPADDING', (0, 1), (0, 1), 20),
    ]))
    elements.append(observacion_table)
    elements.append(Spacer(1, 0.4 * cm))

    # === Declaración y firmas ===
    declaracion_parrafo = Paragraph(
        "El trabajador manifiesta: He recibido los elementos de trabajo anteriormente relacionados en buen estado físico y de funcionamiento..."
        , styles['Normal']
    )
    tabla_final = Table([
        [declaracion_parrafo],
        [Table([
            ['Entregado por:', 'Recibido por:'],
            ['_______________', '_______________'],
            ['Gestión Humana', 'C.C. N°'],
            ['', 'El Trabajador en misión']
        ], colWidths=[8.5*cm, 8.5*cm])]
    ], colWidths=[17*cm])
    tabla_final.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.7, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    elements.append(tabla_final)

    doc.build(elements)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'entrega_{entrega.id}.pdf')