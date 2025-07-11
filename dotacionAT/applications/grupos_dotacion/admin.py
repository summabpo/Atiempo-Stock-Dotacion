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
    list_display = ('cargo', 'cliente', 'ciudad', 'genero', 'creado_por', 'fecha_creacion')
    list_filter = ('cliente', 'ciudad', 'genero')
    search_fields = ('cargo__nombre', 'cliente__nombre', 'ciudad__nombre')
    ordering = ('-fecha_creacion',)
    autocomplete_fields = ('cargo', 'cliente', 'ciudad', 'creado_por')
    inlines = [GrupoDotacionProductoInline]
    
    
    
@admin.register(GrupoDotacionProducto)
class GrupoDotacionProductoAdmin(admin.ModelAdmin):
    list_display = ('grupo', 'producto', 'cantidad')
    list_filter = ('grupo', 'producto')
    autocomplete_fields = ('grupo', 'producto')