from django.db import models

from applications.grupos_dotacion.models import GrupoDotacion  # ajusta el import si es necesario
from applications.productos.models import Producto
from applications.clientes.models import Cliente
from applications.ciudades.models import Ciudad
from applications.grupos_dotacion.models import Cargo
from django.core.exceptions import ValidationError
import re
from django.utils import timezone
# Create your models here.

class EmpleadoDotacion(models.Model):
    cedula = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)
    #ciudad = models.ForeignKey(Ciudad, on_delete=models.PROTECT, default=1)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.PROTECT, blank=True, null=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    cargo  = models.ForeignKey(Cargo, on_delete=models.PROTECT, blank=True, null=True)
    #cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, blank=True, null=True)
    centro_costo = models.CharField(max_length=100)
    sexo = models.CharField(max_length=20)

    talla_camisa = models.CharField(max_length=20, blank=True, null=True)
    cantidad_camisa = models.PositiveIntegerField(default=0, blank=True, null=True)

    talla_pantalon = models.CharField(max_length=20, blank=True, null=True)
    cantidad_pantalon = models.PositiveIntegerField(default=0, blank=True, null=True)

    talla_zapatos = models.CharField(max_length=20, blank=True, null=True)
    
    cantidad_zapatos = models.PositiveIntegerField(default=0, blank=True, null=True)

    cantidad_botas_caucho = models.PositiveIntegerField(default=0, blank=True, null=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nombre} ({self.cedula}) - {self.cargo or "Sin cargo"}'
    
    
    class Meta:
        verbose_name = "Empleado con Dotación"
        verbose_name_plural = "Empleados con Dotación"
        
    class Meta:
        ordering = ['-fecha_registro']
        
        
def validar_periodo(valor):
    """Valida que el periodo tenga el formato MM/YYYY"""
    if not re.match(r'^(0[1-9]|1[0-2])/\d{4}$', valor):
        raise ValidationError('El periodo debe tener el formato MM/YYYY')

class EntregaDotacion(models.Model):
    TIPO_ENTREGA_CHOICES = [
        ('ingreso', 'Por ingreso'),
        ('ley', 'Por ley'),
    ]
    
    empleado = models.ForeignKey(EmpleadoDotacion, on_delete=models.CASCADE, related_name='entregas')
    grupo = models.ForeignKey(GrupoDotacion, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True, null=True)
    periodo = models.CharField(max_length=10, null=True, blank=True)
    tipo_entrega = models.CharField(max_length=10, choices=TIPO_ENTREGA_CHOICES, null=True, blank=True)
    estado = models.CharField(max_length=10, blank=True, null=True)



    def __str__(self):
        return f"Entrega {self.id} - {self.empleado.nombre if self.empleado else 'Sin empleado'}"

    def total_prendas(self):
        return sum(detalle.cantidad for detalle in self.detalles.all())
    
    def normalizar_talla(self, talla):
        if not talla: return None
        talla_normalizada = talla.upper()
        for prefijo in ['TALLA', 'N°', 'NO', 'NUMERO', 'SIZE']:
            talla_normalizada = talla_normalizada.replace(prefijo, '')
        return talla_normalizada.strip().replace(' ', '')
    
    def _obtener_filtro_talla_por_categoria(self, categoria, empleado):
        nombre_categoria = categoria.nombre.upper()
        # print(f"🔍 Analizando categoría: {nombre_categoria}")
        
        # Mapeo de categorías a campos de talla del empleado
        mapeo_tallas = {
            'CAMISA': 'talla_camisa',
            'CAMISAS': 'talla_camisa',
            'PANTALON': 'talla_pantalon',      
            'PANTALONES': 'talla_pantalon',    
            'JEAN': 'talla_pantalon',          
            'JEANS': 'talla_pantalon',         
            'ZAPATO': 'talla_zapatos',
            'ZAPATOS': 'talla_zapatos', 
            'BOTA': 'talla_zapatos',
            'BOTAS': 'talla_zapatos',
        }
        
        #print(f"   Mapeo disponible: {list(mapeo_tallas.keys())}")
        
        # Obtener el campo de talla del empleado según la categoría
        campo_empleado = None
        for key, campo in mapeo_tallas.items():
            if key in nombre_categoria:
                campo_empleado = campo
                #print(f"   ✅ '{key}' encontrado en '{nombre_categoria}' -> mapeado a: {campo}")
                break
        
        if not campo_empleado:
            #print(f"   ❌ NO se encontró mapeo para: {nombre_categoria}")
            return []
        
        # Obtener la talla del empleado
        talla_empleado = getattr(empleado, campo_empleado, None)
        #print(f"   📏 Talla del empleado ({campo_empleado}): {talla_empleado}")
        
        if not talla_empleado:
            #print(f"   ❌ Empleado no tiene talla definida para {campo_empleado}")
            return []
        
        # Buscar productos que coincidan
        productos_categoria = Producto.objects.filter(categoria=categoria)
        #print(f"   📦 Productos en categoría: {productos_categoria.count()}")
        
        productos_coincidentes = []
        for producto in productos_categoria:
            talla_producto = producto.obtener_talla()
            #print(f"      Producto: {producto.nombre} -> Talla: '{talla_producto}'")
            
            # === ¡REEMPLAZA ESTE BLOQUE COMPLETO! ===
            if talla_producto and talla_empleado:
                # Normalizar ambas tallas para comparar (CORREGIDO)
                talla_producto_normalizada = talla_producto.upper().replace('TALLA', '').replace('N°', '').replace('NO', '').replace(' ', '').strip()
                talla_empleado_normalizada = talla_empleado.upper().replace('TALLA', '').replace('N°', '').replace('NO', '').replace(' ', '').strip()
                
                if talla_producto_normalizada == talla_empleado_normalizada:
                    #print(f"      ✅ COINCIDE: {talla_producto} == {talla_empleado}")
                    productos_coincidentes.append(producto)
                else:
                    print(f"      ❌ NO coincide: {talla_producto} != {talla_empleado}")
            else:
                print(f"      ❌ Faltan datos: Producto talla='{talla_producto}', Empleado talla='{talla_empleado}'")
            # === FIN DEL BLOQUE REEMPLAZADO ===
        
        #print(f"   🎯 Productos coincidentes encontrados: {len(productos_coincidentes)}")
        return productos_coincidentes
    
    def obtener_productos_esperados(self):
        """
        Retorna los productos ESPECÍFICOS para este empleado según su talla
        """
        #print(f"\n🎯 ===== INICIANDO ANÁLISIS ENTREGA {self.id} =====")
        #print(f"👤 Empleado: {self.empleado.nombre}")
        #print(f"📏 Tallas: Camisa={self.empleado.talla_camisa}, Pantalon={self.empleado.talla_pantalon}, Zapatos={self.empleado.talla_zapatos}")
        
        if not self.grupo:
            #print("❌ NO tiene grupo asignado")
            return {}
        
        #print(f"📋 Grupo: {self.grupo}")
        
        productos_esperados = {}
        for categoria_grupo in self.grupo.categorias.all():
            #print(f"\n   📁 Categoría del grupo: {categoria_grupo.categoria.nombre}")
            #print(f"   🔢 Cantidad esperada: {categoria_grupo.cantidad}")
            
            productos_coincidentes = self._obtener_filtro_talla_por_categoria(
                categoria_grupo.categoria, 
                self.empleado
            )
            
            for producto in productos_coincidentes:
                if producto.pk in productos_esperados:
                    productos_esperados[producto.pk] += categoria_grupo.cantidad
                else:
                    productos_esperados[producto.pk] = categoria_grupo.cantidad
                #print(f"   ➕ Producto esperado: {producto.nombre} x{categoria_grupo.cantidad}")
        
        #print(f"📊 Total productos esperados: {len(productos_esperados)}")
        return productos_esperados
    
    
    

    def obtener_productos_entregados(self):
        """
        Retorna diccionario con los productos y cantidades entregadas,
        validando que la talla del producto coincida con la del empleado.
        """
        productos_entregados = {}

        for detalle in self.detalles.all():
            producto = detalle.producto
            categoria_nombre = producto.categoria.nombre.upper()

            # Determinar qué campo de talla usar según la categoría
            if 'CAMISA' in categoria_nombre:
                talla_empleado = self.empleado.talla_camisa
            elif any(x in categoria_nombre for x in ['PANTALON', 'JEAN']):
                talla_empleado = self.empleado.talla_pantalon
            elif any(x in categoria_nombre for x in ['ZAPATO', 'BOTA']):
                talla_empleado = self.empleado.talla_zapatos
            else:
                # Categoría sin mapeo: no sumar para evitar falsos completos
                print(f"⚠️ Categoría {categoria_nombre} sin mapeo de talla. Producto ignorado.")
                continue

            # Si el empleado no tiene talla definida para esta categoría, ignorar
            if not talla_empleado:
                print(f"❌ Empleado sin talla definida para {categoria_nombre}. Producto ignorado.")
                continue

            # Obtener y normalizar la talla del producto y la del empleado
            talla_producto = producto.obtener_talla()
            talla_prod_norm = self.normalizar_talla(talla_producto)
            talla_emp_norm = self.normalizar_talla(talla_empleado)

            # Validar coincidencia de tallas
            if talla_prod_norm and talla_emp_norm and talla_prod_norm == talla_emp_norm:
                productos_entregados[producto.pk] = productos_entregados.get(producto.pk, 0) + detalle.cantidad
                #print(f"✅ Contando {producto.nombre} ({detalle.cantidad}) - Talla coincide ({talla_producto})")
            else:
                print(f"❌ Excluyendo {producto.nombre}: talla entregada '{talla_producto}' "
                    f"≠ talla empleado '{talla_empleado}'")

        return productos_entregados
    

    def es_entrega_completa(self):
        #print(f"\n🔍🔍🔍 ANALIZANDO ENTREGA {self.id} - {self.empleado.nombre}")
        
        if not self.grupo:
            #print("❌ Sin grupo - return False")
            return False
            
        esperados = self.obtener_productos_esperados()
        entregados = self.obtener_productos_entregados()
        
        #print(f"📦 Productos ESPERADOS: {esperados}")
        #print(f"📦 Productos ENTREGADOS: {entregados}")
        
        for producto_id, cantidad_esperada in esperados.items():
            cantidad_entregada = entregados.get(producto_id, 0)
            #print(f"   Producto {producto_id}: Esperado {cantidad_esperada}, Entregado {cantidad_entregada}")
            
            if cantidad_entregada < cantidad_esperada:
                producto = Producto.objects.get(pk=producto_id)
                #print(f"❌ FALTANTE: {producto.nombre} - Esperado: {cantidad_esperada}, Entregado: {cantidad_entregada}")
                return False
        
        #print("✅ ENTREGA COMPLETA")
        return True

    def productos_faltantes(self):
        """
        Retorna lista de productos que faltaron en la entrega con sus cantidades
        """
        if not self.grupo:
            return []
            
        esperados = self.obtener_productos_esperados()
        entregados = self.obtener_productos_entregados()
        
        faltantes = []
        for producto_id, cantidad_esperada in esperados.items():
            cantidad_entregada = entregados.get(producto_id, 0)
            if cantidad_entregada < cantidad_esperada:
                producto = Producto.objects.get(pk=producto_id)
                faltantes.append({
                    'producto': producto,
                    'cantidad_faltante': cantidad_esperada - cantidad_entregada
                })
        
        return faltantes
           
    
    
class DetalleEntregaDotacion(models.Model):
    entrega = models.ForeignKey(EntregaDotacion, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"
    
    
    

class HistorialIngresoEmpleado(models.Model):
    empleado = models.ForeignKey(
        'EmpleadoDotacion',
        on_delete=models.PROTECT,
        related_name='historial_ingresos'
    )
    fecha_ingreso = models.DateField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ingreso de {self.empleado.nombre} - {self.fecha_ingreso}"

    class Meta:
        verbose_name = "Historial de Ingreso"
        verbose_name_plural = "Historial de Ingresos"
        ordering = ['-fecha_ingreso']




class FaltanteEntrega(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    entrega = models.ForeignKey(
        EntregaDotacion,
        on_delete=models.CASCADE,
        related_name='faltantes',
        help_text="Entrega original a la que pertenece este faltante"
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='faltantes',
        help_text="Producto que no pudo ser entregado inicialmente"
    )
    cantidad_faltante = models.PositiveIntegerField(
        help_text="Cantidad pendiente por entregar de este producto"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='pendiente',
        help_text="Estado del faltante (Pendiente, Entregado o Cancelado)"
    )
    observaciones = models.TextField(blank=True, null=True)

    def marcar_como_entregado(self):
        """Marca el faltante como entregado y registra la fecha."""
        self.estado = 'entregado'
        self.fecha_resolucion = timezone.now()
        self.save()

    def __str__(self):
        return f"Faltante de {self.producto.nombre} (x{self.cantidad_faltante}) para {self.entrega.empleado}"
    
    class Meta:
        verbose_name = "Faltante de Entrega"
        verbose_name_plural = "Faltantes de Entregas"
        ordering = ['-fecha_registro']