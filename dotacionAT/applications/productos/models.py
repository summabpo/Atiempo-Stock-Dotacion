# productos/models.py
from django.db import models
from django.conf import settings
from ..data.choices_categorias import CATEGORIAS
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)  # Nombre único de la categoría
    

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    categoria = models.CharField(max_length=100, choices=CATEGORIAS, null=True, blank=True)
    # categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    id_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_edicion = models.DateTimeField(auto_now=True)
    usuario_edita = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos_editados')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aquí puedes ajustar la inicialización si es necesario    