from django.contrib import admin
from .models import InventarioBodega
# Register your models here.


@admin.register(InventarioBodega)
class InventarioBodegaAdmin(admin.ModelAdmin):
    list_display = ('bodega', 'producto', 'entradas', 'salidas', 'stock', 'ultima_entrada', 'ultima_salida')
    search_fields = ('bodega__nombre', 'producto__nombre')
    list_filter = ('bodega',)