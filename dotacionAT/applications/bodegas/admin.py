from django.contrib import admin
from .models import Bodega

# Definir una clase para personalizar la interfaz de administración
class BodegaAdmin(admin.ModelAdmin):
    # Especifica los campos que aparecerán en la lista de bodegas
    list_display = ('id_bodega', 'nombre', 'id_ciudad', 'estado', 'fecha_creacion', 'id_usuario_creador', 'id_usuario_editor')
    
    # Especifica los campos por los cuales se puede buscar
    search_fields = ('nombre', 'direccion', 'id_ciudad__nombre')  # Puedes buscar por el nombre de la ciudad también

    # Especifica los filtros disponibles en el panel de administración
    list_filter = ('estado', 'id_ciudad', 'fecha_creacion')

    # Opcionalmente, puedes hacer que los campos se muestren en un solo formulario de edición
    # como si fueran grupos, lo cual es útil si quieres organizar bien los campos.
    fieldsets = (
        (None, {
            'fields': ('nombre', 'direccion', 'id_ciudad', 'estado')
        }),
        ('Usuario', {
            'fields': ('id_usuario_creador', 'id_usuario_editor')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_edicion')
        }),
    )

# Registrar el modelo 'Bodega' con la clase de configuración 'BodegaAdmin'
admin.site.register(Bodega, BodegaAdmin)
