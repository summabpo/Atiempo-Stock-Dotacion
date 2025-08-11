from django.contrib import admin
from .models import Categoria, Producto

# Registrar el modelo Categoria
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id_categoria','nombre','activo', 'id_usuario', 'id_usuario_editor')  # El campo 'descripcion' ya no está en el modelo
    search_fields = ('nombre',)

# Registrar el modelo Producto
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id_producto', 'nombre', 'categoria', 'stock', 'activo', 'id_usuario', 'usuario_edita', 'fecha_creacion')
    list_filter = ('id_usuario', 'activo')
    search_fields = ('nombre',)
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ('id_usuario', 'usuario_edita')