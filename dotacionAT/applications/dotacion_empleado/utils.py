from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.http import FileResponse
from reportlab.pdfgen import canvas
from django.http import FileResponse
from .models import EntregaDotacion, DetalleEntregaDotacion
from django.http import HttpResponse
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import Image
import os
from django.conf import settings
from reportlab.platypus import Image

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