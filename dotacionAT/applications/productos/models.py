# productos/models.py
from django.db import models
from django.conf import settings
from ..data.choices import CATEGORIAS
from ..data.choices import unidadMedida
from django.shortcuts import get_object_or_404
     
class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True, verbose_name="Activo/Inactivo")

    id_usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='categorias_creadas',
        verbose_name="Usuario Creador"
    )
    
    id_usuario_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='categorias_editadas',
        verbose_name="Usuario Editor"
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"        
        
class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    # categoria = models.CharField(max_length=100, choices=CATEGORIAS, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    id_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_edicion = models.DateTimeField(auto_now=True)
    usuario_edita = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos_editados')
    activo = models.BooleanField(default=True, verbose_name="Activo/Inactivo")
    unidad_medida = models.CharField(max_length=100, choices=unidadMedida, null=True, blank=True )
    stock = models.IntegerField(default=0)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.nombre}"

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aquí puedes ajustar la inicialización si es necesario    
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
    def obtener_talla(self):
        """
        Extrae la talla del nombre del producto - CORREGIDO
        """
        nombre = self.nombre.upper()
        
        # 1. Primero buscar patrones específicos de tallas numéricas (botas, zapatos)
        import re
        
        # Para tallas numéricas como "N° 35", "No. 36", "Talla 37"
        patrones_numericos = [
            r'N°\s*(\d{2})',      # N° 35
            r'NO\.\s*(\d{2})',    # No. 36  
            r'NUMERO\s*(\d{2})',  # Numero 37
            r'TALLA\s*(\d{2})',   # Talla 38
            r'SIZE\s*(\d{2})',    # Size 39
        ]
        
        for patron in patrones_numericos:
            match = re.search(patron, nombre)
            if match:
                talla = match.group(1)
                print(f"🔍 {self.nombre} -> Talla numérica encontrada: {talla}")
                return talla
        
        # 2. Buscar tallas de texto como "S", "M", "L", "XL"
        patrones_texto = [
            r'TALLA\s+([SMLX]+)',    # Talla M, Talla XL
            r'SIZE\s+([SMLX]+)',     # Size L, Size XL
            r'\b([SMLX]{1,3})\b',    # S, M, L, XL, XXL (standalone)
        ]
        
        for patron in patrones_texto:
            match = re.search(patron, nombre)
            if match:
                talla = match.group(1)
                print(f"🔍 {self.nombre} -> Talla texto encontrada: {talla}")
                return talla
        
        # 3. Buscar números sueltos (para pantalones)
        numeros_sueltos = re.findall(r'\b(\d{2})\b', nombre)
        if numeros_sueltos:
            print(f"🔍 {self.nombre} -> Número suelto encontrado: {numeros_sueltos[0]}")
            return numeros_sueltos[0]
        
        print(f"🔍 {self.nombre} -> No se pudo extraer talla")
        return None       