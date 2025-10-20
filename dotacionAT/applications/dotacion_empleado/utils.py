from io import BytesIO
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from django.http import FileResponse, HttpResponse
from reportlab.pdfgen import canvas
from .models import EntregaDotacion, DetalleEntregaDotacion, HistorialIngresoEmpleado, EmpleadoDotacion
import os
from django.conf import settings
import pandas as pd
from django.db import transaction
from django.utils import timezone
from applications.ciudades.models import Ciudad
from applications.grupos_dotacion.models import Cargo
from applications.grupos_dotacion.models import Cargo
from applications.clientes.models import Cliente
from datetime import timedelta
from django.utils.timezone import now
from collections import Counter


def obtener_talla_para_categoria(categoria, empleado):
    nombre = categoria.nombre.lower().strip()
    print(f"🔎 Categoria detectada: '{nombre}'")
    print(f"Empleado: {empleado.nombre} (Camisa={empleado.talla_camisa}, "
          f"Pantalón={empleado.talla_pantalon}, Zapatos={empleado.talla_zapatos})")

    if "camisa" in nombre:
        return empleado.talla_camisa
    elif "jean" in nombre or "pantalon" in nombre:
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

def safe_str(value):
    try:
        return str(value).strip()
    except Exception:
        return ""

def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def generar_formato_entrega_pdf(request):
    
    ruta_logo = os.path.join(settings.BASE_DIR, 'applications', 'ciudades', 'static', 'index', 'img', 'logoAtiempo.png')
    logo = Image(ruta_logo, width=80, height=40) if os.path.exists(ruta_logo) else ''
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    styles = getSampleStyleSheet()

    # Estilos personalizados
    title_style = ParagraphStyle(name='TitleCenter', parent=styles['Title'], alignment=1, fontSize=14)
    normal_bold = ParagraphStyle(name='NormalBold', parent=styles['Normal'], fontSize=10, leading=12, spaceAfter=4, fontName='Helvetica-Bold')

    entregas = EntregaDotacion.objects.select_related('empleado', 'grupo').prefetch_related('detalles__producto').all()

    for entrega in entregas:
        empleado = entrega.empleado
        
        parrafo_estilo = ParagraphStyle(
        name="TablaWrap",
        fontSize=9,
        leading=10,  # Espaciado entre líneas
        wordWrap='CJK',  # Permite cortar palabras largas
        alignment=1,  # Centrado
        fontName='Helvetica-Bold'
    )

        # --- Encabezado tipo tabla organizado como en el Word ---
        encabezado_data = [
            ['Código: FOR-GC-007', Paragraph('FORMATO DE ENTREGA ELEMENTOS DE TRABAJO', parrafo_estilo), logo],
            ['Versión: 02', '', ''],
            ['Fecha vigencia: 02/04/2019', '', '']
        ]

        encabezado_table = Table(encabezado_data, colWidths=[4.8*cm, 8.7*cm, 3.5*cm])
        encabezado_table.setStyle(TableStyle([
            # Unir verticalmente columnas para título y logo
            ('SPAN', (1, 0), (1, 2)),
            ('SPAN', (2, 0), (2, 2)),

            # Bordes de tabla (cuadrícula completa)
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),

            # Alineaciones
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (0, 1), (0, 1), 'LEFT'),
            ('ALIGN', (0, 2), (0, 2), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'CENTER'),

            # Estilos de texto
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),

            # Espaciado interno
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(encabezado_table)
        elements.append(Spacer(1, 0.5 * cm))
        colWidths=[5.5*cm, 8*cm, 3.5*cm]
        suma_total = sum(colWidths)
        print(f"Suma total: {suma_total/cm:.2f} cm")
        
        parrafo_estilo = ParagraphStyle(
        name="TablaWrap",
        fontSize=9,
        leading=10,  # Espaciado entre líneas
        wordWrap='CJK',  # Permite cortar palabras largas
    )

        # === Tabla con información del trabajador ===
        datos_trabajador = [
        ['Nombre Trabajador', Paragraph(empleado.nombre, parrafo_estilo), 'N.° ID', str(empleado.cedula)],
        ['Empresa', Paragraph(str(empleado.cliente), parrafo_estilo), 'Cargo', Paragraph(str(empleado.cargo), parrafo_estilo)],
        ['Fecha Ingreso',
        empleado.fecha_ingreso.strftime("%d/%m/%Y") if empleado.fecha_ingreso else '',
        'Fecha de entrega',
        f"{entrega.fecha_entrega.strftime('%m/%Y')}  |  Periodo: " f"{entrega.periodo}"  ]
    ]
        tabla_datos = Table(datos_trabajador, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
        tabla_datos.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('WORDWRAP', (0, 0), (-1, -1), 'CJK'),
        ]))
        
        elements.append(tabla_datos)
        elements.append(Spacer(1, 0.5 * cm))
        
        colWidths2= [3.5*cm, 5*cm, 3.5*cm, 5*cm]
        suma_total = sum(colWidths2)
        print(f"Suma total: {suma_total/cm:.2f} cm")

        checkbox_texto = Paragraph("Se hace entrega de los siguientes elementos de trabajo:", styles['Normal'])

        checkboxes_data = [
            [checkbox_texto, '', '', ''],  # Fila 1 con celda combinada
            ['[X] DOTACIÓN', '[ ] EPP', '[ ] HERRAMIENTAS', '[ ] OTROS']  # Fila 2
        ]

        tabla_checkbox = Table(checkboxes_data, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
        tabla_checkbox.setStyle(TableStyle([
            # Combinar toda la primera fila en una sola celda
            ('SPAN', (0, 0), (3, 0)),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),

            # Espaciado mínimo (sin tanto top)
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),

            # Alineaciones
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (0, 1), (0, 1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Fuente
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))

        elements.append(tabla_checkbox)
        elements.append(Spacer(1, 0.5 * cm))

        subtitulo = ['ARTÍCULO', 'CANTIDAD']
        tabla_data = [subtitulo]
        for detalle in entrega.detalles.all():
            producto = detalle.producto
            tabla_data.append([producto.nombre, str(detalle.cantidad)])

        tabla = Table(tabla_data, colWidths=[12*cm, 5*cm])  # Ajuste aquí
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 0.8, colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(tabla)
        elements.append(Spacer(1, 0.5 * cm))

        # --- Observaciones con recuadro y espacio para escribir ---
        # --- Cuadro de observaciones ---
        observacion = entrega.observaciones or " "
        observacion_table = Table([
            [Paragraph("<b>OBSERVACIONES:</b> Espacio para reportar novedades en la entrega de los elementos que sea relevante mencionar:", styles['Normal'])],
            [Paragraph(observacion, styles['Normal'])]
        ], colWidths=[17*cm])

        observacion_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (0, 0), 4),
            ('BOTTOMPADDING', (0, 0), (0, 0), 4),
            ('TOPPADDING', (0, 1), (0, 1), 20),  # Espacio para escribir
            ('BOTTOMPADDING', (0, 1), (0, 1), 20),
        ]))
        elements.append(observacion_table)
        elements.append(Spacer(1, 0.4 * cm))

        # --- Declaración del trabajador ---
        declaracion_estilo = ParagraphStyle(
            name="DeclaracionEstilo",
            fontSize=9,
            leading=11,
            spaceAfter=6,
        )

        # Texto de la declaración
        declaracion_parrafo = Paragraph(
            "El trabajador manifiesta:<br/>"
            "He recibido los elementos de trabajo anteriormente relacionados en buen estado físico y de funcionamiento. "
            "Me comprometo a cumplir con las especificaciones dadas por Seguridad y Salud en el Trabajo, a ejercer la debida custodia "
            "y cuidado como bienes de la empresa, puestos bajo mi responsabilidad. A la terminación del contrato o en cualquier momento que la empresa me lo solicite, "
            "igualmente me comprometo a devolverlos en buen estado de funcionamiento.",
            declaracion_estilo
        )

        # Tabla final que incluye declaración + firmas en un solo recuadro
        tabla_final = Table([
            [declaracion_parrafo],
            [  # Fila firmas
                Table([
                    ['Entregado por:', 'Recibido por:'],
                    ['_______________', '_______________'],
                    ['Gestión Humana', 'C.C. N°'],
                    ['', 'El Trabajador en misión']
                ], colWidths=[8.5*cm, 8.5*cm], hAlign='CENTER')
            ]
        ], colWidths=[17*cm])

        tabla_final.setStyle(TableStyle([
            # Borde general externo
            ('GRID', (0, 0), (-1, -1), 0.7, colors.black),

            # Espaciado dentro del recuadro general
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),

            # Fuente interna (tabla de firmas)
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))

        elements.append(tabla_final)

        elements.append(PageBreak())

    doc.build(elements)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='entregas_dotacion.pdf')

def generar_pdf_entregas(entregas):
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    )
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from io import BytesIO
    import os

    # === Inicialización general ===
    ruta_logo = os.path.join(settings.BASE_DIR, 'applications', 'ciudades', 'static', 'index', 'img', 'logoAtiempo.png')
    logo = Image(ruta_logo, width=80, height=40) if os.path.exists(ruta_logo) else ''

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
            ['Fecha Ingreso',
             empleado.fecha_ingreso.strftime("%d/%m/%Y") if empleado.fecha_ingreso else '',
             'Fecha de entrega',
             f"{entrega.fecha_entrega.strftime('%m/%Y')} | Periodo: {entrega.periodo}"]
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
            [Paragraph("<b>OBSERVACIONES:</b> Espacio para reportar novedades en la entrega:", styles['Normal'])],
            [Paragraph(observacion, styles['Normal'])]
        ], colWidths=[17 * cm])
        observacion_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
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
            [['Entregado por:', 'Recibido por:']],
        ], colWidths=[17 * cm])
        tabla_final.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.7, colors.black),
        ]))
        elements.append(tabla_final)

        # Salto de página
        elements.append(PageBreak())

    # === Generar el PDF ===
    doc.build(elements)
    buffer.seek(0)
    return buffer

def crear_historial_ingreso_inicial(empleado):
    """
    Crea el registro inicial de historial de ingreso
    cuando se crea un empleado por primera vez.
    """
    HistorialIngresoEmpleado.objects.create(
        empleado=empleado,
        cliente=empleado.cliente,
        ciudad=empleado.ciudad,
        cargo=empleado.cargo,
        centro_costo=empleado.centro_costo,
        fecha_ingreso=empleado.fecha_ingreso,
        observaciones="Ingreso inicial"
    )
         
def limpiar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza el DataFrame:
    - Elimina filas completamente vacías
    - Normaliza nombres de columnas (mayúsculas, convierte ". " a "._", convierte espacios a "_",
      mantiene '.' y '_' y elimina caracteres raros)
    - Normaliza strings en las celdas (strip + upper) evitando SettingWithCopyWarning
    - Detecta columnas de fecha y las convierte a datetime (con dayfirst=True)
    """
    # Trabajar sobre copia para evitar warnings
    df = df.dropna(how="all").copy()

    # Normalizar nombres de columnas en varios pasos
    cols = df.columns.astype(str).str.strip().str.upper()

    # 1) Reemplazar ". " o ".\s+" por "._" -> convierte "C. COSTO" -> "C._COSTO"
    cols = cols.str.replace(r'\.\s+', '._', regex=True)

    # 2) Reemplazar espacios (uno o más) por guion bajo
    cols = cols.str.replace(r'\s+', '_', regex=True)

    # 3) Reemplazar cualquier caracter que no sea A-Z, 0-9, '_' o '.' por '_'
    cols = cols.str.replace(r'[^A-Z0-9._]', '_', regex=True)

    # 4) Colapsar múltiples "_" en uno solo
    cols = cols.str.replace(r'_+', '_', regex=True)

    # 5) Asegurarnos de que no queden "_" al inicio/final
    cols = cols.str.strip('_')

    df.columns = cols

    # Rellenar NaN
    df = df.fillna('')

    # Normalizar valores de tipo string
    for col in df.select_dtypes(include=['object']).columns:
        df.loc[:, col] = df[col].astype(str).str.strip().str.upper()

    # 🔥 Conversión automática de columnas de fecha
    for col in df.columns:
        if "FECHA" in col or "INGRESO" in col:  # puedes ajustar si tienes otros nombres
            try:
                df[col] = pd.to_datetime(
                    df[col], errors="coerce", dayfirst=True
                )
            except Exception:
                pass  # si no se puede convertir, se deja como está

    return df

def obtener_o_crear_empleado(fila):
    """
    Crea o recupera un empleado a partir de una fila del Excel.
    - Usa los FK de Cargo, Cliente y Ciudad existentes.
    - Si es nuevo, registra historial de ingreso.
    - Si ya existía y cambia la fecha de ingreso, guarda historial adicional.
    """

    cedula = safe_str_number(fila.get("NUMERO_DE_DOCUMENTO"))
    if not cedula:
        return None

    # --- Buscar relaciones ---
    cargo = Cargo.objects.filter(nombre__iexact=safe_str(fila.get("CARGO"))).first() if fila.get("CARGO") else None
    cliente = Cliente.objects.filter(nombre__iexact=safe_str(fila.get("CLIENTE"))).first() if fila.get("CLIENTE") else None
    ciudad = Ciudad.objects.filter(nombre__iexact=safe_str(fila.get("CENTRO_TRABAJO"))).first() if fila.get("CENTRO_TRABAJO") else None

    centro_costo = safe_str(fila.get("C._COSTO")) or "N/A"

    # --- Parsear fecha ---
    fecha_ingreso = fila.get("INGRESO")
    if pd.notna(fecha_ingreso):
        try:
            if isinstance(fecha_ingreso, str):
                fecha_ingreso = pd.to_datetime(fecha_ingreso, dayfirst=True, errors="coerce")
            elif isinstance(fecha_ingreso, (int, float)):
                fecha_ingreso = pd.to_datetime(fecha_ingreso, errors="coerce", unit="d", origin="1899-12-30")
            fecha_ingreso = fecha_ingreso.date() if pd.notna(fecha_ingreso) else None
        except Exception:
            fecha_ingreso = None
    else:
        fecha_ingreso = None

    # --- Crear o recuperar ---
    empleado, creado = EmpleadoDotacion.objects.get_or_create(
        cedula=cedula,
        defaults={
            "nombre": safe_str(fila.get("NOMBRE_COMPLETO")),
            "sexo": safe_str(fila.get("SEXO")),
            "talla_camisa": safe_str(fila.get("TALLA_CAMISA")),
            "talla_pantalon": safe_str(fila.get("TALLA_PANTALON")),
            "talla_zapatos": safe_str(fila.get("TALLA_ZAPATOS")),
            "cargo": cargo,
            "cliente": cliente,
            "ciudad": ciudad,
            "centro_costo": centro_costo,
            "fecha_ingreso": fecha_ingreso,
            "cantidad_camisa": int(fila.get("CANTIDAD_CAMISA", 0) or 0),
            "cantidad_pantalon": int(fila.get("CANTIDAD_PANTALON", 0) or 0),
            "cantidad_zapatos": int(fila.get("CANTIDAD_ZAPATOS", 0) or 0),
            "cantidad_botas_caucho": int(fila.get("BOTAS_CAUCHO", 0) or 0),
        }
    )

    # --- Si ya existía ---
    if not creado:
        cambios = False

        # Detectar cambio en fecha de ingreso
        if fecha_ingreso and empleado.fecha_ingreso != fecha_ingreso:
            HistorialIngresoEmpleado.objects.create(
                empleado=empleado,
                fecha_ingreso=fecha_ingreso,
            )
            empleado.fecha_ingreso = fecha_ingreso
            cambios = True

        # Actualizar FKs si estaban vacíos
        if not empleado.cargo and cargo:
            empleado.cargo = cargo
            cambios = True
        if not empleado.cliente and cliente:
            empleado.cliente = cliente
            cambios = True
        if not empleado.ciudad and ciudad:
            empleado.ciudad = ciudad
            cambios = True

        if cambios:
            empleado.save()

    # --- Si es nuevo, registrar historial inicial ---
    if creado:
        HistorialIngresoEmpleado.objects.create(
            empleado=empleado,
            fecha_ingreso=fecha_ingreso or timezone.now().date(),
        )

    return empleado

def crear_entrega_dotacion(empleado, grupo, tipo_entrega, periodo=None):
    """
    Aplica las reglas de negocio para generar la entrega de dotación.
    Retorna la entrega creada o None si no corresponde generar.
    """

    tipo_entrega_lower = tipo_entrega.lower()  # normalizamos para comparar con choices

    # --- Caso entrega por ingreso ---
    if tipo_entrega_lower == "ingreso":
        ingreso_actual = HistorialIngresoEmpleado.objects.filter(
            empleado=empleado
        ).order_by("-fecha_ingreso").first()

        if not ingreso_actual:
            return None  # no hay ingreso registrado

        # ✅ Validar si ya existe entrega por ley (significa que ya pasó su ingreso anterior)
        if EntregaDotacion.objects.filter(
            empleado=empleado,
            tipo_entrega="ley"
        ).exists():
            return None  # ya tuvo una entrega de ley, no se permite ingreso

        # validar si ya existe entrega para ese mismo ingreso
        existe_entrega = EntregaDotacion.objects.filter(
            empleado=empleado,
            tipo_entrega="ingreso",
            periodo=ingreso_actual.fecha_ingreso  # mismo ingreso
        ).exists()

        if existe_entrega:
            return None  # ya tenía entrega por este ingreso

        # crear la entrega
        return EntregaDotacion.objects.create(
            empleado=empleado,
            grupo=grupo,
            tipo_entrega="ingreso",
            periodo=ingreso_actual.fecha_ingreso
        )

    # --- Caso entrega por ley ---
    elif tipo_entrega_lower == "ley":
        ultimo_ingreso = HistorialIngresoEmpleado.objects.filter(
            empleado=empleado
        ).order_by("-fecha_ingreso").first()

        if not ultimo_ingreso:
            return None  # nunca ha ingresado, no corresponde

        # validar antigüedad >= 90 días
        dias_transcurridos = (now().date() - ultimo_ingreso.fecha_ingreso).days
        if dias_transcurridos < 90:
            return None  # aún no cumple la antigüedad mínima

        # validar que no exista entrega en el mismo periodo
        if EntregaDotacion.objects.filter(
            empleado=empleado,
            tipo_entrega="ley",
            periodo=periodo
        ).exists():
            return None

        # crear la entrega
        return EntregaDotacion.objects.create(
            empleado=empleado,
            grupo=grupo,
            tipo_entrega="ley",
            periodo=periodo
        )

    return None

def reconstruir_productos_esperados(grupo_productos, tallas_empleado):
    """
    Construye un diccionario { (categoria, talla): cantidad_esperada } a partir
    de los productos del grupo y las tallas del empleado.
    """
    productos_esperados = Counter()

    for gp in grupo_productos:  # gp: instancia de GrupoDotacionProducto
        categoria = gp.categoria.nombre.strip().upper()

        # Determinar la talla según la categoría
        if "CAMISA" in categoria:
            talla = tallas_empleado.get("camisa")
        elif "JEAN" in categoria or "PANTALON" in categoria:
            talla = tallas_empleado.get("pantalon")
        elif "BOTA" in categoria or "ZAPATO" in categoria:
            talla = tallas_empleado.get("zapato")
        else:
            talla = "ÚNICA"

        clave = (categoria, talla)
        productos_esperados[clave] += gp.cantidad

    return productos_esperados