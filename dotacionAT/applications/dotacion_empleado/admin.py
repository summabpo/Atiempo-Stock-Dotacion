from django.contrib import admin
from .models import EmpleadoDotacion, EntregaDotacion, DetalleEntregaDotacion, HistorialIngresoEmpleado, FaltanteEntrega
from applications.grupos_dotacion.models import GrupoDotacion, GrupoDotacionProducto

# Register your models here.

# Inline para mostrar el historial dentro del empleado
class HistorialIngresoEmpleadoInline(admin.TabularInline):  # puedes usar StackedInline si prefieres
    model = HistorialIngresoEmpleado
    extra = 1  # cuántos registros vacíos quieres que aparezcan listos para añadir
    fields = ['fecha_ingreso']
    ordering = ['-fecha_ingreso']

# Admin de empleado con el inline
@admin.register(EmpleadoDotacion)
class EmpleadoDotacionAdmin(admin.ModelAdmin):
    list_display = ("cedula", "nombre", "cargo", "cliente", "ciudad", "fecha_ingreso")
    search_fields = ("cedula", "nombre")
    list_filter = ("cargo", "cliente", "ciudad", "sexo")
    ordering = ['-fecha_registro']
    inlines = [HistorialIngresoEmpleadoInline]

# Admin del historial por si quieres gestionarlo independiente
@admin.register(HistorialIngresoEmpleado)
class HistorialIngresoEmpleadoAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'fecha_ingreso', 'fecha_registro')
    search_fields = ('empleado__nombre', 'empleado__cedula')
    list_filter = ('fecha_ingreso', 'empleado__cliente', 'empleado__ciudad')
    ordering = ['-fecha_ingreso']

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
        'estado',
        'empleado_cliente',
        'empleado_sexo',
        'grupo_dotacion',
        'fecha_entrega',
        'productos_entregados',
        
    )
    list_filter = ('fecha_entrega',)
    search_fields = ('id', 'empleado__nombre', 'empleado__cedula', 'grupo_dotacion__cliente__nombre')
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

@admin.register(FaltanteEntrega)
class FaltanteEntregaAdmin(admin.ModelAdmin):
    # Campos visibles en la lista
    list_display = (
        'empleado_relacionado',  # ← método para mostrar empleado
        'producto',
        'cantidad_faltante',
        'estado',
        'fecha_registro',
        'fecha_resolucion',
    )
    list_filter = ('estado', 'fecha_registro')
    search_fields = (
        'entrega__empleado__nombre',  # Busca por nombre del empleado
        'producto__nombre',
        'observaciones',
    )
    ordering = ('-fecha_registro',)

    def empleado_relacionado(self, obj):
        """Muestra el empleado asociado a la entrega."""
        return obj.entrega.empleado
    empleado_relacionado.short_description = "Empleado"    