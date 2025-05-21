from django.contrib import admin
from .models import Salida, ItemSalida


class ItemSalidaInline(admin.TabularInline):
    model = ItemSalida
    extra = 1
    readonly_fields = ['subtotal_formateado']
    fields = ['producto', 'cantidad', 'precio_unitario', 'subtotal_formateado']
    show_change_link = False


@admin.register(Salida)
class SalidaAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo_documento', 'fecha_creacion', 'total', 'estado']
    # list_filter = ['tipo_documento', 'fecha_creacion', 'estado']
    search_fields = ['numero_factura', 'cliente__nombre']
    inlines = [ItemSalidaInline]
    date_hierarchy = 'fecha_creacion'
    ordering = ['-fecha_creacion']
    fieldsets = (
        ('Información General', {
            'fields': ('tipo_documento',  'cliente', 'bodega', 'estado')
        }),
        ('Detalle Financiero', {
            'fields': ('total', 'observaciones')
        }),
    )


@admin.register(ItemSalida)
class ItemSalidaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'salida', 'cantidad', 'precio_unitario', 'subtotal_formateado', 'tipo_documento']
    # list_filter = ['salida__tipo_documento']
    search_fields = ['producto__nombre']
    readonly_fields = ['subtotal_formateado']

    def tipo_documento(self, obj):
        return obj.salida.get_tipo_documento_display()
    tipo_documento.short_description = 'Tipo de Documento'