import threading
import re
from applications.inventario.models import  InventarioBodega
from django.utils import timezone
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse, JsonResponse, FileResponse
from django.contrib import messages
import pandas as pd
from .models import EmpleadoDotacion, EntregaDotacion, DetalleEntregaDotacion, FaltanteEntrega
from applications.grupos_dotacion.models import GrupoDotacion, GrupoDotacionProducto
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
from openpyxl import load_workbook
from io import BytesIO
from django.utils.timezone import now
from crum import set_current_user, get_current_user
from django.db.models import Q, F, Func, Value, CharField, Count, Case, When, BooleanField, Subquery, OuterRef
from datetime import datetime
from django.db.models import Count, Sum
from applications.dotacion_empleado.utils import generar_pdf_entregas
from urllib.parse import unquote
from django.db.models.functions import Replace, Upper, Concat, TruncMinute
from django.template.loader import render_to_string
import pdfkit  # o WeasyPrint, xhtml2pdf, etc.
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from collections import defaultdict
from applications.ciudades.utils import normalizar_ciudad
 
 

def get_or_none(modelo, **filtros):
    try:
        return modelo.objects.get(**filtros)
    except modelo.DoesNotExist:
        return None

def descontar_stock_directo(productos_entregados, bodega):
    for detalle in productos_entregados:
        try:
            inventario = InventarioBodega.objects.get(
                bodega=bodega,
                producto=detalle.producto
            )
            
            cantidad = detalle.cantidad or 0
            if cantidad <= 0:
                continue

            # 🧾 Actualizar inventario
            inventario.salidas += cantidad
            inventario.stock -= cantidad
            inventario.ultima_salida = timezone.now()
            inventario.usuario_ultima_salida = getattr(detalle.entrega, "usuario_creador", None)
            inventario.save()

            # 🔁 Actualizar stock total del producto (sumando todas las bodegas)
            producto = detalle.producto
            stock_total = InventarioBodega.objects.filter(producto=producto).aggregate(
                total=Sum('stock')
            )['total'] or 0
            producto.stock = stock_total
            producto.save(update_fields=['stock'])

        except InventarioBodega.DoesNotExist:
            print(f"❌ No existe inventario para {detalle.producto.nombre} en {bodega.nombre}")
            continue
        
    
def historial_entregas2(request):
    entregas = EntregaDotacion.objects.select_related('empleado', 'grupo_dotacion') \
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
def list_empleados(request):
    if request.user.rol == 'almacen' and request.user.sucursal:
        # Comparación insensible a mayúsculas/minúsculas con icontains
        empleadoDotacion = EmpleadoDotacion.objects.filter(ciudad__nombre__icontains=request.user.sucursal.nombre)
    else:
        empleadoDotacion = EmpleadoDotacion.objects.all()

    data = {
        'empleado': [
            {
                'cedula': c.cedula,
                'nombre': c.nombre,
                'ciudad': c.ciudad.nombre if c.ciudad else "Sin ciudad",
                'cargo': c.cargo.nombre if c.cargo else "Sin cargo",
                'cliente': c.cliente.nombre if c.cliente else "Sin cliente",
                'centro_costo': c.centro_costo,
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
    # --- Parámetros GET ---
    periodo = request.GET.get('periodo')
    cliente_id = request.GET.get('cliente_id')
    tipo_entrega = request.GET.get('tipo_entrega')
    centro_costo = request.GET.get('centro_costo')
    ciudad = request.GET.get('ciudad')

    # print(f"🔎 Parámetros recibidos -> periodo={periodo}, cliente_id={cliente_id}, tipo_entrega={tipo_entrega}, centro_costo={centro_costo}, ciudad={ciudad}")

    entregas = (
        EntregaDotacion.objects
        .select_related('empleado__cliente',  'empleado__ciudad', 'grupo_dotacion')
        .prefetch_related('detalles__producto')
        .order_by('-fecha_entrega')
    )

    # --- FILTRAR POR PERÍODO ---
    if periodo:
        try:
            if '-' in periodo and len(periodo.split('-')) == 3:
                fecha = datetime.strptime(periodo, "%Y-%m-%d")
                periodo_formateado = fecha.strftime("%m/%Y")
                # print(f"🔄 Período convertido: {periodo} -> {periodo_formateado}")
                entregas = entregas.filter(
                    Q(periodo=periodo) | Q(periodo=periodo_formateado)
                )
            else:
                entregas = entregas.filter(periodo=periodo)
                # print(f"🔍 Buscando período: {periodo}")
        except ValueError as e:
            # print(f"⚠️ Error al parsear el período: {e}")
            entregas = entregas.filter(periodo=periodo)

    # --- FILTRAR POR CLIENTE ---
    cliente_nombre = None
    if cliente_id:
        try:
            entregas = entregas.filter(empleado__cliente__id_cliente=int(cliente_id))
            cliente_obj = Cliente.objects.filter(id_cliente=cliente_id).first()
            cliente_nombre = cliente_obj.nombre if cliente_obj else None
            print(f"👤 Filtrado por cliente ID: {cliente_id}")
        except (ValueError, TypeError):
            print(f"⚠️ ID de cliente inválido: {cliente_id}")

    # --- FILTRAR POR TIPO DE ENTREGA ---
    if tipo_entrega:
        entregas = entregas.filter(tipo_entrega=tipo_entrega)
        # print(f"🎯 Filtrado por tipo: {tipo_entrega}")

    # --- FILTRAR POR CENTRO DE COSTO ---
    if centro_costo:
        entregas = entregas.filter(empleado__centro_costo__iexact=centro_costo)
        # print(f"🏢 Filtrado por centro de costo: {centro_costo}")

    # --- FILTRAR POR CIUDAD ---
    if ciudad:
        entregas = entregas.filter(empleado__ciudad__iexact=ciudad)
        # print(f"🌆 Filtrado por ciudad: {ciudad}")

    print(f"📦 Entregas encontradas después de filtros: {entregas.count()}")

    if entregas.exists():
        periodos_unicos = entregas.values_list('periodo', flat=True).distinct()
        # print(f"📊 Períodos únicos en resultados: {list(periodos_unicos)}")

    return render(
        request,
        'historial_entregas.html',
        {
            'entregas': entregas,
            'periodo': periodo,
            'cliente': cliente_nombre,
            'tipo_entrega': tipo_entrega,
            'centro_costo': centro_costo,
            'ciudad': ciudad,
        }
    )


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
        # form = CargarArchivoForm(request.POST, request.FILES)
        form = CargarArchivoForm(request.POST, request.FILES, user=request.user)
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
                    'SEXO', 'TALLA_CAMISA', 'TALLA_PANTALON', 'TALLA_ZAPATOS', 'RETIRO'
                ]
                faltantes = [col for col in columnas_requeridas if col not in df.columns]
                if faltantes:
                    messages.error(request, f"❌ Faltan columnas en el archivo: {faltantes}")
                    return render(request, 'cargar_empleados.html', {'form': form})

                contador, entregas = 0, 0
                
                df["RETIRO"] = df["RETIRO"].astype(str).str.strip().str.upper()

                # 🔹 Registrar empleados inactivos o retirados
                empleados_inactivos = df[df["RETIRO"] != "VIGENTE"]
                for _, fila in empleados_inactivos.iterrows():
                    cedula = safe_str(fila['NUMERO_DE_DOCUMENTO']).strip()
                    nombre = fila['NOMBRE_COMPLETO']
                    empleados_sin_entrega.append(f"{nombre} ({cedula}) - Empleado inactivo o retirado")

                # 🔹 Filtrar solo empleados vigentes
                total_inicial = len(df)
                df = df[df["RETIRO"] == "VIGENTE"]
                descartados = total_inicial - len(df)

                if descartados > 0:
                    messages.info(request, f"ℹ️ Se omitieron {descartados} empleados no vigentes (RETIRO ≠ 'VIGENTE').")

                if df.empty:
                    messages.warning(request, "⚠️ No hay empleados con estado 'VIGENTE' para procesar.")
                    return render(request, 'cargar_empleados.html', {'form': form})

                # try:
                #     bodega_dotacion = Bodega.objects.get(nombre__iexact="Principal")
                # except Bodega.DoesNotExist:
                #     messages.error(request, "❌ No se encontró la bodega 'Principal'.")
                #     return render(request, 'cargar_empleados.html', {'form': form})
                # 🔹 Determinar la bodega según el tipo de entrega
                if tipo_entrega.lower() == "ley":
                    try:
                        bodega_dotacion = Bodega.objects.get(nombre__iexact="Principal")
                    except Bodega.DoesNotExist:
                        messages.error(request, "❌ No se encontró la bodega 'Principal'.")
                        return render(request, 'cargar_empleados.html', {'form': form})
                else:
                    # Para entregas de tipo "ingreso", usar la sucursal asociada al usuario
                    if request.user.sucursal:
                        bodega_dotacion = request.user.sucursal
                    else:
                        messages.error(request, "⚠️ No tienes una bodega asignada en tu perfil de usuario. Asigna una sucursal para continuar.")
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
                    # Normalizar el nombre de la ciudad antes del filtro
                    # Normalizar el nombre de la ciudad antes del filtro
                    if empleado.ciudad:
                        nombre_ciudad = normalizar_ciudad(empleado.ciudad.nombre)
                    else:
                        nombre_ciudad = None

                    if nombre_ciudad:
                        variantes_ciudad = {
                            nombre_ciudad,
                            nombre_ciudad.lower(),
                            nombre_ciudad.upper(),
                            nombre_ciudad.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
                        }

                        grupos = GrupoDotacion.objects.filter(
                            cargos=cargo_obj,
                            cliente=empleado.cliente,
                            genero__iexact=empleado.sexo,
                            ciudades__nombre__in=variantes_ciudad
                        ).distinct()
                    else:
                        grupos = GrupoDotacion.objects.none()

                    if not grupos.exists():
                        empleados_sin_entrega.append(f"{empleado.nombre} ({cedula}) - Sin grupo de dotación")
                        sin_grupo.append(f"{empleado.nombre} ({cedula}) - Sin grupo de dotación")
                        continue

                    grupo = grupos.first()
                    productos = GrupoDotacionProducto.objects.filter(grupo=grupo)

                    entrega = crear_entrega_dotacion(empleado, grupo, tipo_entrega, periodo, bodega_dotacion)
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

                   # Si no hay nada entregado, eliminamos la entrega
                    # Si no hay nada entregado, eliminamos la entrega y aseguramos que 'motivo' exista
                    if not productos_entregados:
                        # Asignamos un motivo claro antes de usarlo
                        if productos_sin_stock:
                            motivo = f"Sin stock para: {', '.join(productos_sin_stock)}"
                        else:
                            motivo = "Sin stock total"

                        try:
                            entrega.delete()
                        except Exception:
                            pass

                        empleados_sin_entrega.append(f"{empleado.nombre} ({cedula}) - {motivo}")
                        sin_stock.append(f"{empleado.nombre} ({cedula}) - {motivo}")
                        continue

                    # 🔹 Marcar estado de la entrega según lo entregado y lo faltante
                    if productos_sin_stock:
                        entrega.estado = "parcial"
                    else:
                        entrega.estado = "completa"
                    entrega.save()
                    
                   
                    # --- Crear registros de faltantes con cantidad detectada ---
                    for faltante in productos_sin_stock:
                        # Detectar la cantidad (ej. "requerido 2")
                        match = re.search(r"requerido\s+(\d+)", faltante, re.IGNORECASE)
                        cantidad = int(match.group(1)) if match else 1

                        # Obtener el nombre base del producto (sin " - requerido X")
                        nombre_base = faltante.split(" - ")[0].strip()

                        # ✅ Buscar la talla que corresponde al empleado para esta categoría
                        talla_empleado = obtener_talla_para_categoria(producto_grupo.categoria, empleado)

                        # Buscar el producto correcto en función de la talla del empleado
                        producto_real = Producto.objects.filter(
                            categoria=producto_grupo.categoria,
                            nombre__icontains=talla_empleado
                        ).first()

                        if producto_real:
                            FaltanteEntrega.objects.create(
                                entrega=entrega,
                                producto=producto_real,  # ✅ ahora se guarda la talla correcta
                                cantidad_faltante=cantidad,
                                estado='pendiente',
                            )
                        else:
                            advertencias.append(
                                f"No se encontró Producto para faltante: {producto_grupo.categoria.nombre} talla {talla_empleado}"
                            )
                    

                    # 🔹 Continuar con la salida
                    # generar_salida_por_entrega(entrega, productos_entregados, request.user)
                    descontar_stock_directo(productos_entregados, bodega_dotacion)
                    entregas += 1

                    if productos_sin_stock:
                        motivo = f"Sin stock para: {', '.join(productos_sin_stock)}"
                        empleados_sin_entrega.append(f"{empleado.nombre} ({cedula}) - {motivo}")

                # --- Mensaje resumen y detalles en plantilla ---
                if contador > 0:
                    resumen = f"✅ Se procesaron {contador} filas y se generaron {entregas} entregas."
                    messages.success(request, resumen)

                    # Agrupar empleados sin entrega por motivo
                    motivos_dict = defaultdict(list)
                    for e in empleados_sin_entrega:
                        nombre_cedula, sep, motivo = e.rpartition(" - ")
                        if not motivo:
                            motivo = "Motivo no especificado"
                        nombre = nombre_cedula.split("(")[0].strip()
                        cedula = nombre_cedula[nombre_cedula.find("(")+1 : nombre_cedula.find(")")]
                        motivos_dict[motivo].append({
                            "nombre": nombre,
                            "cedula": cedula
                        })

                    return render(request, "cargar_empleados_resultado.html", {
                        "mensaje": resumen,
                        "motivos_dict": dict(motivos_dict),
                    })

                else:
                    messages.warning(request, "⚠️ No se procesó ninguna fila válida.")
                    return redirect("cargar_empleados")

            except Exception as e:
                messages.error(request, f"❌ Error al procesar el archivo: {str(e)}")
                return redirect("cargar_empleados")

    else:
        form = CargarArchivoForm(user=request.user)

    return render(request, 'cargar_empleados.html', {
        'form': form,
    })


def progreso_carga(request):
    progreso = cache.get('progreso_carga', {"total": 1, "actual": 0})
    porcentaje = int((progreso["actual"] / progreso["total"]) * 100) if progreso["total"] > 0 else 0
    return JsonResponse({"progreso": porcentaje})


def descargar_pdf_entrega(request, entrega_id):
    entrega = get_object_or_404(EntregaDotacion, pk=entrega_id)
    return generar_formato_entrega_pdf(entrega)


def vista_consolidado(request):
    entregas = EntregaDotacion.objects.all()

    # 👷 Filtro por rol y sucursal (solo ve su bodega)
    if request.user.rol == 'almacen' and request.user.sucursal:
        entregas = entregas.filter(bodega=request.user.sucursal)
        print(f"👷 Usuario Almacén -> filtrando por su bodega: {request.user.sucursal.nombre}")
        print(f"📦 Entregas visibles: {entregas.count()}")
    else:
        print(f"👑 Usuario {request.user.rol} -> sin filtro de bodega (ve todo)")

    # 📊 Consolidado final (ya no usamos Subquery)
    consolidado = (
        entregas
        .annotate(
            fecha_minuto=TruncMinute('fecha_entrega'),
        )
        .values(
            'empleado__cliente__nombre',
            'empleado__cliente__id_cliente',
            'empleado__ciudad__id_ciudad',
            'empleado__ciudad__nombre',
            'empleado__centro_costo',
            'bodega__nombre',  # ✅ ahora se toma directo del modelo
            'periodo',
            'tipo_entrega',
            'fecha_minuto',
        )
        .annotate(
            total_entregas=Count('id'),
            parciales=Count('id', filter=Q(estado='parcial')),
            completas=Count('id', filter=Q(estado='completa')),
        )
        .annotate(
            tiene_parciales=Case(
                When(parciales__gt=0, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        )
        .order_by(
            'empleado__cliente__nombre',
            'empleado__ciudad__nombre',
            'empleado__centro_costo',
            'periodo',
            'tipo_entrega',
            'fecha_minuto',
        )
    )

    return render(request, "consolidado.html", {"consolidado": consolidado})


# Función para reemplazar caracteres en DB
class Replace(Func):
    function = 'REPLACE'
    arity = 3

def generar_pdf_por_periodo(request):
    # Obtener parámetros de la URL
    periodo = request.GET.get('periodo')
    cliente_id = request.GET.get('cliente_id')
    tipo_entrega = request.GET.get('tipo_entrega')
    centro_costo = request.GET.get('centro_costo')  # Nuevo
    ciudad = request.GET.get('ciudad')              # Nuevo

    print(f"DEBUG - periodo: {periodo}, cliente_id: {cliente_id}, tipo: {tipo_entrega}, "
           f"centro_costo: {centro_costo}, ciudad: {ciudad}")

    # Validar parámetros mínimos obligatorios
    if not periodo or not cliente_id or not tipo_entrega:
        return HttpResponse("Faltan parámetros requeridos: periodo, cliente_id y tipo_entrega", status=400)

    try:
        cliente_id_int = int(cliente_id)
    except (ValueError, TypeError):
        return HttpResponse("ID de cliente inválido", status=400)

    # Filtro base
    filtros = {
        "periodo": periodo,
        "empleado__cliente__id_cliente": cliente_id_int,
        "tipo_entrega": tipo_entrega
    }

    # Agregar filtros dinámicamente si vienen
    if centro_costo:
        filtros["empleado__centro_costo__icontains"] = centro_costo  # usa icontains por si no es exacto
    if ciudad:
        filtros["empleado__ciudad__icontains"] = ciudad

    # Aplicar filtro
    entregas = EntregaDotacion.objects.filter(**filtros).select_related(
        'empleado__cliente', 'grupo_dotacion'
    ).prefetch_related('detalles__producto')

    if not entregas.exists():
        return HttpResponse(
            f"No hay entregas para los parámetros dados: {filtros}",
            status=404
        )
    
    print(f"DEBUG - Entregas encontradas: {entregas.count()}")

    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    )
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from io import BytesIO
    from reportlab.platypus import Spacer
    from django.http import FileResponse
    import os

    # === Inicialización general ===
    ruta_logo = os.path.join(settings.BASE_DIR, 'applications', 'ciudades', 'static', 'index', 'img', 'logoAtiempo.png')
    logo = Image(ruta_logo, width=80, height=40) if os.path.exists(ruta_logo) else Spacer(1, 40)

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm
    )

    elements = []
    styles = getSampleStyleSheet()

    # Estilos personalizados
    parrafo_estilo = ParagraphStyle(
        name="TablaWrap",
        fontSize=9,
        leading=10,
        wordWrap='CJK'
    )

    # === Recorrer entregas y armar contenido ===
    for entrega in entregas:
        empleado = entrega.empleado

        # --- Encabezado ---
        encabezado_data = [
            ['Código: FOR-GC-007', Paragraph('FORMATO DE ENTREGA ELEMENTOS DE TRABAJO', parrafo_estilo), logo],
            ['Versión: 02', '', ''],
            ['Fecha vigencia: 02/04/2019', '', '']
        ]
        encabezado_table = Table(encabezado_data, colWidths=[4.8 * cm, 8.7 * cm, 3.5 * cm])
        encabezado_table.setStyle(TableStyle([
            ('SPAN', (1, 0), (1, 2)),
            ('SPAN', (2, 0), (2, 2)),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'CENTER'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
        ]))
        elements.append(encabezado_table)
        elements.append(Spacer(1, 0.5 * cm))

        # --- Datos trabajador ---
        datos_trabajador = [
            ['Nombre Trabajador', Paragraph(empleado.nombre, parrafo_estilo), 'N.° ID', str(empleado.cedula)],
            ['Empresa', Paragraph(str(empleado.cliente), parrafo_estilo), 'Cargo', Paragraph(str(empleado.cargo), parrafo_estilo)],
            ['Ciudad', Paragraph(str(empleado.ciudad), parrafo_estilo), 'Centro de Costo', Paragraph(str(empleado.centro_costo), parrafo_estilo)],
            ['Fecha Ingreso',
            empleado.fecha_ingreso.strftime("%d/%m/%Y") if empleado.fecha_ingreso else '',
            'Fecha de entrega',
            f"{entrega.fecha_entrega.strftime('%m/%Y')}  |  Periodo: {entrega.periodo}" ]
        ]
        tabla_datos = Table(datos_trabajador, colWidths=[3.5 * cm, 5 * cm, 3.5 * cm, 5 * cm])
        tabla_datos.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('WORDWRAP', (0, 0), (-1, -1), 'CJK'),
        ]))
        elements.append(tabla_datos)
        elements.append(Spacer(1, 0.5 * cm))

        # --- Checkbox ---
        checkbox_texto = Paragraph("Se hace entrega de los siguientes elementos de trabajo:", styles['Normal'])
        checkboxes_data = [
            [checkbox_texto, '', '', ''],
            ['[X] DOTACIÓN', '[ ] EPP', '[ ] HERRAMIENTAS', '[ ] OTROS']
        ]
        tabla_checkbox = Table(checkboxes_data, colWidths=[3.5 * cm, 5 * cm, 3.5 * cm, 5 * cm])
        tabla_checkbox.setStyle(TableStyle([
            ('SPAN', (0, 0), (3, 0)),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        elements.append(tabla_checkbox)
        elements.append(Spacer(1, 0.5 * cm))

        # --- Detalles ---
        tabla_data = [['ARTÍCULO', 'CANTIDAD']]
        for detalle in entrega.detalles.all():
            tabla_data.append([detalle.producto.nombre, str(detalle.cantidad)])
        tabla = Table(tabla_data, colWidths=[12 * cm, 5 * cm])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.8, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        elements.append(tabla)
        elements.append(Spacer(1, 0.5 * cm))

        # --- Observaciones ---
        observacion = entrega.observaciones or " "
        observacion_table = Table([
            [Paragraph("<b>OBSERVACIONES:</b>", styles['Normal'])],
            [Paragraph(observacion or " ", styles['Normal'])]
        ], colWidths=[17 * cm])
        observacion_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('TOPPADDING', (0, 1), (0, 1), 20),
            ('BOTTOMPADDING', (0, 1), (0, 1), 20),
        ]))
        elements.append(observacion_table)
        elements.append(Spacer(1, 0.4 * cm))

        # --- Declaración y firmas ---
        declaracion_parrafo = Paragraph(
            "El trabajador manifiesta:<br/>"
            "He recibido los elementos en buen estado y me comprometo a cuidarlos...",
            ParagraphStyle(name="DeclaracionEstilo", fontSize=9, leading=11)
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
        ]))
        elements.append(tabla_final)

        # Salto de página
        elements.append(PageBreak())

    # === Generar el PDF ===
    # doc.build(elements)
    # buffer.seek(0)
    # return FileResponse(
    #     buffer,
    #     as_attachment=True,
    #     filename=f"entregas_{periodo}_{cliente_id}.pdf"
    # )
    doc.build(elements)
    buffer.seek(0)

    # --- Crear nombre dinámico y seguro ---
    safe_periodo = periodo.replace('/', '-').replace(' ', '_')
    safe_tipo = tipo_entrega.replace(' ', '_')
    # También puedes incluir el nombre del cliente si prefieres
    cliente = entregas.first().empleado.cliente.nombre
    safe_cliente = str(cliente).replace(' ', '_')
    # Centro de costo
    centro_costo_val = entregas.first().empleado.centro_costo or "SinCentroCosto"
    safe_centro = str(centro_costo_val).replace(' ', '_').replace('/', '-')
    filename = f"dotacion_{safe_periodo}_{safe_tipo}_{safe_cliente}_{safe_centro}.pdf"

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=filename
    )

def generar_pdf_por_entrega(request, entrega_id):
    entrega = get_object_or_404(
        EntregaDotacion.objects.select_related('empleado', 'grupo_dotacion').prefetch_related('detalles__producto'),
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
        ['Nombre Trabajador', Paragraph(empleado.nombre, parrafo_estilo), 'N.° ID', str(empleado.cedula)],
        ['Empresa', Paragraph(str(empleado.cliente), parrafo_estilo), 'Cargo', Paragraph(str(empleado.cargo), parrafo_estilo)],
        ['Ciudad', Paragraph(str(empleado.ciudad), parrafo_estilo), 'Centro de Costo', Paragraph(str(empleado.centro_costo), parrafo_estilo)],
        ['Fecha Ingreso',
        empleado.fecha_ingreso.strftime("%d/%m/%Y") if empleado.fecha_ingreso else '',
        'Fecha de entrega',
        f"{entrega.fecha_entrega.strftime('%m/%Y')}  |  Periodo: {entrega.periodo}" ]
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
    
    # --- Armar nombre del archivo ---
    cedula = empleado.cedula.replace(" ", "_")  
    proyecto = str(empleado.cliente).replace(" ", "_")  
    centro_costo = str(empleado.centro_costo).replace(" ", "_") if empleado.centro_costo else "sinCC"
    fecha = entrega.fecha_entrega.strftime("%Y%m%d") if entrega.fecha_entrega else "sin_fecha"

    filename = f"{cedula}_{proyecto}_{centro_costo}_{fecha}.pdf"

    doc.build(elements)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=filename)



# def generar_entrega_faltantes(request, entrega_id):
#     """
#     Genera la entrega de los productos faltantes de una entrega parcial.
#     Solo entrega los productos exactos que están en FaltanteEntrega
#     y cuya talla coincide con la talla del empleado.
#     """
#     entrega = get_object_or_404(EntregaDotacion, id=entrega_id)
#     faltantes = FaltanteEntrega.objects.filter(entrega=entrega, estado='pendiente')

#     if not faltantes.exists():
#         messages.info(request, "Esta entrega no tiene faltantes pendientes.")
#         return redirect('historial_entregas')

#     # Obtener bodega principal
#     try:
#         bodega = Bodega.objects.get(nombre__iexact='Principal')
#     except Bodega.DoesNotExist:
#         messages.error(request, "❌ No se encontró la bodega 'Principal'.")
#         return redirect('historial_entregas')

#     entregados, no_stock = [], []

#     for faltante in faltantes:
#         producto = faltante.producto
#         categoria_nombre = producto.categoria.nombre.upper()

#         # 🧩 Determinar talla del empleado según categoría
#         if 'CAMISA' in categoria_nombre:
#             talla_empleado = entrega.empleado.talla_camisa
#         elif any(x in categoria_nombre for x in ['PANTALON', 'JEAN']):
#             talla_empleado = entrega.empleado.talla_pantalon
#         elif any(x in categoria_nombre for x in ['ZAPATO', 'BOTA']):
#             talla_empleado = entrega.empleado.talla_zapatos
#         else:
#             talla_empleado = None

#         # Extraer tallas numéricas (cuando aplican)
#         talla_prod = re.findall(r'\d+', producto.nombre)
#         talla_emp = re.findall(r'\d+', talla_empleado or '')

#         talla_producto = talla_prod[0] if talla_prod else None
#         talla_empleado = talla_emp[0] if talla_emp else talla_empleado  # usa texto si no hay número

#         # ❌ Si la talla del producto no coincide con la del empleado → no entregar
#         if talla_producto and talla_empleado and talla_producto != talla_empleado:
#             no_stock.append(
#                 f"{producto.nombre} - talla producto {talla_producto} ≠ talla empleado {talla_empleado}"
#             )
#             continue

#         try:
#             inventario = InventarioBodega.objects.get(bodega=bodega, producto=producto)

#             if inventario.stock >= faltante.cantidad_faltante:
#                 # ✅ Crear detalle de entrega solo del producto faltante exacto
#                 DetalleEntregaDotacion.objects.create(
#                     entrega=entrega,
#                     producto=producto,
#                     cantidad=faltante.cantidad_faltante
#                 )

#                 # Actualizar inventario y faltante
#                 inventario.stock -= faltante.cantidad_faltante
#                 inventario.save()

#                 faltante.estado = 'entregado'
#                 faltante.fecha_resolucion = timezone.now()
#                 faltante.save()

#                 entregados.append(f"{producto.nombre} x{faltante.cantidad_faltante}")
#             else:
#                 no_stock.append(f"{producto.nombre} (Stock insuficiente)")

#         except InventarioBodega.DoesNotExist:
#             no_stock.append(f"{producto.nombre} (Sin registro en bodega)")

#     # Si ya no hay faltantes pendientes, marcar la entrega como completa
#     if not FaltanteEntrega.objects.filter(entrega=entrega, estado='pendiente').exists():
#         entrega.estado = 'completa'
#         entrega.save()

#     # ✅ Mensajes al usuario
#     if entregados:
#         messages.success(request, f"✅ Se entregaron: {', '.join(entregados)}.")
#     if no_stock:
#         messages.warning(request, f"⚠️ No se entregaron: {', '.join(no_stock)}.")

#     return redirect('vista_consolidado')



# def generar_entrega_faltantes(request, entrega_id):
#     """
#     Genera la entrega de los productos faltantes de una entrega parcial.
#     Solo entrega productos cuya talla coincida con la talla del empleado.
#     """
#     entrega = get_object_or_404(EntregaDotacion, id=entrega_id)
#     faltantes = FaltanteEntrega.objects.filter(entrega=entrega, estado='pendiente')

#     if not faltantes.exists():
#         messages.info(request, "Esta entrega no tiene faltantes pendientes.")
#         return redirect('historial_entregas')

#     # 🏢 Determinar bodega según el usuario
#     bodega_usuario = getattr(request.user, 'bodega', None)
#     if bodega_usuario:
#         bodega = bodega_usuario
#     else:
#         try:
#             bodega = Bodega.objects.get(nombre__iexact='Principal')
#         except Bodega.DoesNotExist:
#             messages.error(request, "❌ No se encontró la bodega asociada ni la 'Principal'.")
#             return redirect('historial_entregas')

#     entregados = []
#     no_stock = []

#     # Extraer talla del empleado (puede incluir texto como 'N° 40')
#     talla_empleado_match = re.search(r'(\d+)', entrega.empleado.talla_zapatos or '')
#     talla_empleado = talla_empleado_match.group(1) if talla_empleado_match else None

#     for faltante in faltantes:
#         try:
#             # Verificamos inventario del producto faltante exacto
#             inventario = InventarioBodega.objects.get(bodega=bodega, producto=faltante.producto)

#             # 📌 Extraer talla numérica del producto faltante
#             talla_producto_match = re.search(r'(\d+)', faltante.producto.nombre)
#             talla_producto = talla_producto_match.group(1) if talla_producto_match else None

#             # ❌ Si ambas tallas existen y no coinciden, saltar
#             if talla_producto and talla_empleado and talla_producto != talla_empleado:
#                 no_stock.append(
#                     f"Excluida {faltante.producto.nombre}: talla entregada {talla_producto} ≠ talla empleado {talla_empleado}"
#                 )
#                 continue

#             # ✅ Si hay stock suficiente, entregar
#             if inventario.stock >= faltante.cantidad_faltante:
#                 DetalleEntregaDotacion.objects.create(
#                     entrega=entrega,
#                     producto=faltante.producto,
#                     cantidad=faltante.cantidad_faltante
#                 )
#                 inventario.stock -= faltante.cantidad_faltante
#                 inventario.save()

#                 faltante.estado = 'entregado'
#                 faltante.fecha_resolucion = timezone.now()
#                 faltante.save()

#                 entregados.append(faltante.producto.nombre)
#             else:
#                 no_stock.append(f"{faltante.producto.nombre} (Faltan {faltante.cantidad_faltante})")

#         except InventarioBodega.DoesNotExist:
#             no_stock.append(f"{faltante.producto.nombre} (Sin registro en bodega)")

#     # Si ya no hay faltantes pendientes, marcamos la entrega como completa
#     if not FaltanteEntrega.objects.filter(entrega=entrega, estado='pendiente').exists():
#         entrega.estado = 'completa'
#         entrega.save()

#     # ✅ Mensajes al usuario
#     if entregados:
#         messages.success(request, f"✅ Se entregaron: {', '.join(entregados)}.")
#     if no_stock:
#         messages.warning(request, f"⚠️ Sin stock o talla incorrecta para: {', '.join(no_stock)}.")

#     return redirect('vista_consolidado')



@transaction.atomic
def generar_entrega_faltantes(request, entrega_id):
    """
    Genera la entrega de los productos faltantes de una entrega parcial.
    Afecta el inventario directamente (usando descontar_stock_directo)
    y actualiza el estado de la entrega cuando ya no quedan pendientes.
    """
    entrega = get_object_or_404(EntregaDotacion, id=entrega_id)
    faltantes = FaltanteEntrega.objects.filter(entrega=entrega, estado='pendiente')

    if not faltantes.exists():
        messages.info(request, "Esta entrega no tiene faltantes pendientes.")
        return redirect('historial_entregas')

    # 🏢 Determinar bodega desde el usuario
    bodega = getattr(request.user, 'sucursal', None)
    if not bodega:
        try:
            bodega = Bodega.objects.get(nombre__iexact='Principal')
        except Bodega.DoesNotExist:
            messages.error(request, "❌ No se encontró la bodega del usuario ni la 'Principal'.")
            return redirect('historial_entregas')

    entregados = []
    no_stock = []
    productos_entregados = []

    for faltante in faltantes:
        producto = faltante.producto
        categoria_nombre = producto.categoria.nombre.upper()

        # 🧩 Determinar talla del empleado según categoría
        if 'CAMISA' in categoria_nombre:
            talla_empleado = entrega.empleado.talla_camisa
        elif any(x in categoria_nombre for x in ['PANTALON', 'JEAN']):
            talla_empleado = entrega.empleado.talla_pantalon
        elif any(x in categoria_nombre for x in ['ZAPATO', 'BOTA']):
            talla_empleado = entrega.empleado.talla_zapatos
        else:
            talla_empleado = None

        # Extraer tallas numéricas
        talla_prod = re.findall(r'\d+', producto.nombre)
        talla_emp = re.findall(r'\d+', talla_empleado or '')

        talla_producto = talla_prod[0] if talla_prod else None
        talla_empleado = talla_emp[0] if talla_emp else talla_empleado

        # ⚠️ Si las tallas no coinciden, saltar
        if talla_producto and talla_empleado and talla_producto != talla_empleado:
            no_stock.append(
                f"{producto.nombre} - talla producto {talla_producto} ≠ talla empleado {talla_empleado}"
            )
            continue

        try:
            inventario = InventarioBodega.objects.get(bodega=bodega, producto=producto)

            if inventario.stock >= faltante.cantidad_faltante:
                # ✅ Crear detalle y agregar a lista de entregados
                detalle = DetalleEntregaDotacion.objects.create(
                    entrega=entrega,
                    producto=producto,
                    cantidad=faltante.cantidad_faltante
                )
                productos_entregados.append(detalle)

                # Marcar faltante como entregado
                faltante.estado = 'entregado'
                faltante.fecha_resolucion = timezone.now()
                faltante.save()

                entregados.append(f"{producto.nombre} x{faltante.cantidad_faltante}")
            else:
                no_stock.append(f"{producto.nombre} (Stock insuficiente en {bodega.nombre})")

        except InventarioBodega.DoesNotExist:
            no_stock.append(f"{producto.nombre} (No existe en inventario de {bodega.nombre})")

    # 🧾 Descontar stock de todos los productos entregados
    if productos_entregados:
        try:
            descontar_stock_directo(productos_entregados, bodega)
        except Exception as e:
            messages.error(request, f"❌ Error al descontar stock: {e}")

    # ✅ Si ya no hay faltantes pendientes, marcar entrega como completa
    if not FaltanteEntrega.objects.filter(entrega=entrega, estado='pendiente').exists():
        entrega.estado = 'completa'
        entrega.save()

    # 📢 Mensajes de resultado
    if entregados:
        messages.success(request, f"✅ Se entregaron desde {bodega.nombre}: {', '.join(entregados)}.")
    if no_stock:
        messages.warning(request, f"⚠️ No se entregaron: {', '.join(no_stock)}.")

    return redirect('vista_consolidado')