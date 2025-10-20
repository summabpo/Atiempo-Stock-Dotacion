from django.contrib import admin
from .models import InventarioBodega
# Register your models here.

@admin.register(InventarioBodega)
class InventarioBodegaAdmin(admin.ModelAdmin):
    list_display = ('bodega', 'producto', 'producto_id_display', 'entradas', 'salidas', 'stock', 'ultima_entrada', 'ultima_salida', 'usuario_ultima_salida', 'usuario_ultima_entrada')
    search_fields = ('bodega__nombre', 'producto__nombre')
    list_filter = ('bodega',)

    @admin.display(description='ID Producto')
    def producto_id_display(self, obj):
        return obj.producto.pk if obj.producto else 'N/A'