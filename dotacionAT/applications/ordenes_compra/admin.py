from django.contrib import admin
from .models import OrdenCompra, ItemOrdenCompra, Compra, ItemCompra, DiferenciaTraslado

class detalleOrdenInline(admin.TabularInline):
    model = ItemOrdenCompra
    extra = 1

@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'estado', 'tipo_documento', 'total', 'usuario_creador', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('proveedor__nombre',)
    inlines = [detalleOrdenInline]

@admin.register(ItemOrdenCompra)
class ItemOrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('orden', 'producto', 'cantidad', 'tipo_documento', 'precio_unitario', 'usuario_orden')

    def usuario_orden(self, obj):
        return obj.orden.usuario_creador  # 👈 accede al usuario de la orden
    usuario_orden.short_description = 'Usuario Creador'
    
class ItemCompraInline(admin.TabularInline):
    model = ItemCompra
    extra = 0  # No muestra filas vacías adicionales
    readonly_fields = ('subtotal',)  # Opcional, si quieres mostrar el subtotal

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'orden_compra', 'tipo_documento', 'proveedor', 'total', 'bodega', 'estado', 'numero_factura', 'fecha_creacion', 'fecha_compra', 'usuario_creador', 'observaciones')
    search_fields = ('orden_compra__id', 'orden_compra__proveedor__nombre', 'numero_factura')
    inlines = [ItemCompraInline]
    readonly_fields = ('fecha_creacion',)

@admin.register(ItemCompra)
class ItemCompraAdmin(admin.ModelAdmin):
    list_display = (
        'compra',
        'producto_id_display',
        'numero_factura',
        'fecha_compra',
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

    def fecha_compra(self, obj):
        return obj.compra.fecha_compra
    fecha_compra.short_description = 'Fecha de Compra'
    
    
    @admin.display(description='ID Producto')
    def producto_id_display(self, obj):
        return obj.producto.pk if obj.producto else 'N/A'  
    

@admin.register(DiferenciaTraslado)
class DiferenciaTrasladoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'producto',
        'salida',
        'compra',
        'cantidad_enviada',
        'cantidad_recibida',
        'diferencia',
        'resuelto',
        'fecha_registro',
    )
    list_filter = (
        'resuelto',
        'fecha_registro',
        'salida__bodegaSalida',
        'compra__bodega',
    )
    search_fields = (
        'producto__nombre',
        'salida__id',
        'compra__id',
        'observacion',
    )
    readonly_fields = ('diferencia', 'fecha_registro')
    list_editable = ('resuelto', 'cantidad_recibida')
    ordering = ('-fecha_registro',)
    list_per_page = 25
    date_hierarchy = 'fecha_registro'
    fieldsets = (
        ('Información del Traslado', {
            'fields': ('salida', 'compra', 'producto')
        }),
        ('Cantidades', {
            'fields': ('cantidad_enviada', 'cantidad_recibida', 'diferencia')
        }),
        ('Estado y Observaciones', {
            'fields': ('resuelto', 'observacion', 'fecha_registro')
        }),
    )

    def get_queryset(self, request):
        """Optimiza el query para evitar consultas repetidas."""
        qs = super().get_queryset(request)
        return qs.select_related('salida', 'compra', 'producto')

    def save_model(self, request, obj, form, change):
        """Recalcula la diferencia antes de guardar desde el admin."""
        obj.diferencia = obj.cantidad_enviada - obj.cantidad_recibida
        super().save_model(request, obj, form, change)