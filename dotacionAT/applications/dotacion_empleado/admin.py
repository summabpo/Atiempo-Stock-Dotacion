from django.contrib import admin
from .models import EmpleadoDotacion, EntregaDotacion, EntregaDotacion, DetalleEntregaDotacion
from applications.grupos_dotacion.models import GrupoDotacion, GrupoDotacionProducto

# Register your models here.

@admin.register(EmpleadoDotacion)
class EmpleadoDotacionAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombre', 'cliente', 'fecha_ingreso', 'fecha_registro')
    search_fields = ('cedula', 'nombre', 'cliente')
    

# @admin.register(EntregaDotacion)
# class EntregaDotacionAdmin(admin.ModelAdmin):
#     list_display = (
#         'empleado_nombre',
#         'empleado_cedula',
#         'empleado_ciudad',
#         'empleado_cargo',
#         'empleado_cliente',
#         'empleado_sexo',
#         'grupo',
#         'fecha_entrega',
#         'productos_entregados',
#     )
#     list_filter = ('grupo__genero', 'fecha_entrega', 'grupo__cliente')
#     search_fields = ('empleado__nombre', 'empleado__cedula', 'grupo__cliente__nombre')

#     def empleado_nombre(self, obj):
#         return obj.empleado.nombre if obj.empleado else "Sin empleado"
#     empleado_nombre.short_description = 'Empleado'

#     def empleado_cedula(self, obj):
#         return obj.empleado.cedula if obj.empleado else "-"
#     empleado_cedula.short_description = 'Cédula'

#     def empleado_ciudad(self, obj):
#         return obj.empleado.ciudad if obj.empleado else "-"
#     empleado_ciudad.short_description = 'Ciudad'

#     def empleado_cargo(self, obj):
#         return obj.empleado.cargo if obj.empleado else "-"
#     empleado_cargo.short_description = 'Cargo'

#     def empleado_cliente(self, obj):
#         return obj.empleado.cliente if obj.empleado else "-"
#     empleado_cliente.short_description = 'Cliente'

#     def empleado_sexo(self, obj):
#         return obj.empleado.sexo if obj.empleado else "-"
#     empleado_sexo.short_description = 'Sexo'

#     def productos_entregados(self, obj):
#         if obj.grupo:
#             productos = obj.grupo.productos.all()
#             return ", ".join([f"{p.producto.nombre} x{p.cantidad}" for p in productos])
#         return "Sin grupo"
#     productos_entregados.short_description = "Prendas Entregadas"


# Inline para mostrar los detalles (productos entregados) dentro del admin de EntregaDotacion
class DetalleEntregaDotacionInline(admin.TabularInline):
    model = DetalleEntregaDotacion
    extra = 0
    autocomplete_fields = ['producto']
    readonly_fields = ('producto', 'cantidad')  # Puedes quitar esto si deseas editar

@admin.register(EntregaDotacion)
class EntregaDotacionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'empleado_nombre',
        'empleado_cedula',
        'empleado_ciudad',
        'empleado_cargo',
        'periodo',
        'tipo_entrega',
        'empleado_cliente',
        'empleado_sexo',
        'grupo',
        'fecha_entrega',
        'productos_entregados',
    )
    list_filter = ('fecha_entrega',)
    search_fields = ('id', 'empleado__nombre', 'empleado__cedula', 'grupo__cliente__nombre')
    inlines = [DetalleEntregaDotacionInline]
    date_hierarchy = 'fecha_entrega'

    def empleado_nombre(self, obj):
        return obj.empleado.nombre if obj.empleado else "-"
    empleado_nombre.short_description = 'Empleado'

    def empleado_cedula(self, obj):
        return obj.empleado.cedula if obj.empleado else "-"
    empleado_cedula.short_description = 'Cédula'

    def empleado_ciudad(self, obj):
        return obj.empleado.ciudad if obj.empleado else "-"
    empleado_ciudad.short_description = 'Ciudad'

    def empleado_cargo(self, obj):
        return obj.empleado.cargo if obj.empleado else "-"
    empleado_cargo.short_description = 'Cargo'

    def empleado_cliente(self, obj):
        return obj.empleado.cliente if obj.empleado else "-"
    empleado_cliente.short_description = 'Cliente'

    def empleado_sexo(self, obj):
        return obj.empleado.sexo if obj.empleado else "-"
    empleado_sexo.short_description = 'Sexo'

    def productos_entregados(self, obj):
        detalles = obj.detalles.all()  # accede a DetalleEntregaDotacion
        if detalles.exists():
            return ", ".join([f"{d.producto.nombre} x{d.cantidad}" for d in detalles])
        return "Sin productos"
    productos_entregados.short_description = "Prendas Entregadas"

@admin.register(DetalleEntregaDotacion)
class DetalleEntregaDotacionAdmin(admin.ModelAdmin):
    list_display = ('entrega', 'producto', 'cantidad')
    search_fields = ('producto__nombre', 'entrega__empleado__nombre')
    list_filter = ('producto',)