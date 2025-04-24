from django.contrib import admin
from .models import OrdenCompra, ItemOrdenCompra

class detalleOrdenInline(admin.TabularInline):
    model = ItemOrdenCompra
    extra = 1

@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('proveedor__nombre',)
    inlines = [detalleOrdenInline]

@admin.register(ItemOrdenCompra)
class ItemOrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('orden', 'producto', 'cantidad', 'precio_unitario')