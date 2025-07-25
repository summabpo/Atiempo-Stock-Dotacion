from django.contrib import admin
from .models import GrupoDotacion, GrupoDotacionProducto, Cargo


class GrupoDotacionProductoInline(admin.TabularInline):
    model = GrupoDotacionProducto
    extra = 1

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    search_fields = ('nombre', 'activo')
    ordering = ('nombre',)

@admin.register(GrupoDotacion)
class GrupoDotacionAdmin(admin.ModelAdmin):
    list_display = ('mostrar_cargos', 'mostrar_cliente', 'mostrar_ciudades', 'genero', 'creado_por', 'fecha_creacion')
    list_filter = ('cliente', 'ciudades', 'genero')
    search_fields = ('cargos__nombre', 'cliente__nombre', 'ciudades__nombre')
    ordering = ('-fecha_creacion',)
    autocomplete_fields = ('cargos', 'cliente', 'ciudades', 'creado_por')
    inlines = [GrupoDotacionProductoInline]

    def mostrar_cargos(self, obj):
        return ", ".join([c.nombre for c in obj.cargos.all()])
    mostrar_cargos.short_description = "Cargos"

    def mostrar_cliente(self, obj):
        return obj.cliente.nombre if obj.cliente else "—"
    mostrar_cliente.short_description = "Cliente"

    def mostrar_ciudades(self, obj):
        return ", ".join([c.nombre for c in obj.ciudades.all()])
    mostrar_ciudades.short_description = "Ciudades"
    
    
    
@admin.register(GrupoDotacionProducto)
class GrupoDotacionProductoAdmin(admin.ModelAdmin):
    list_display = ('grupo', 'producto', 'cantidad')
    list_filter = ('grupo', 'producto')
    autocomplete_fields = ('grupo', 'producto')