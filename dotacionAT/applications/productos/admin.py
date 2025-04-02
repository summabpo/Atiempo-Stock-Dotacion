from django.contrib import admin
from .models import Categoria, Producto

# Registrar el modelo Categoria
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)  # El campo 'descripcion' ya no está en el modelo
    search_fields = ('nombre',)

# Registrar el modelo Producto
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'id_usuario', 'fecha_creacion')  # El campo 'precio' ya no está en el modelo
    list_filter = ('categoria', 'id_usuario')
    search_fields = ('nombre', 'categoria__nombre', 'descripcion')  # 'descripcion' aún está en la búsqueda
    date_hierarchy = 'fecha_creacion'