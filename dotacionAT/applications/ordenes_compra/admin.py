from django.contrib import admin
from .models import OrdenCompra, ItemOrdenCompra, Compra, ItemCompra
class detalleOrdenInline(admin.TabularInline):
    model = ItemOrdenCompra
    extra = 1

@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'estado', 'tipo_documento', 'total', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('proveedor__nombre',)
    inlines = [detalleOrdenInline]

@admin.register(ItemOrdenCompra)
class ItemOrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('orden', 'producto', 'cantidad', 'tipo_documento', 'precio_unitario')
    
    
class ItemCompraInline(admin.TabularInline):
    model = ItemCompra
    extra = 0  # No muestra filas vacías adicionales
    readonly_fields = ('subtotal',)  # Opcional, si quieres mostrar el subtotal

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'orden_compra', 'tipo_documento', 'total', 'bodega', 'estado', 'numero_factura', 'fecha_recepcion')
    search_fields = ('orden_compra__id', 'orden_compra__proveedor__nombre', 'numero_factura')
    inlines = [ItemCompraInline]
    readonly_fields = ('fecha_recepcion',)

@admin.register(ItemCompra)
class ItemCompraAdmin(admin.ModelAdmin):
    list_display = (
        'compra',
        'numero_factura',
        'fecha_recepcion',
        'producto',
        'cantidad_recibida',
        'precio_unitario',
        'subtotal_formateado',
        'tipo_documento'
    )
    search_fields = ('producto__nombre', 'compra__id')

    def numero_factura(self, obj):
        return obj.compra.numero_factura
    numero_factura.short_description = 'N° Factura'

    def fecha_recepcion(self, obj):
        return obj.compra.fecha_recepcion
    fecha_recepcion.short_description = 'Fecha Recepción'  
    
    
    