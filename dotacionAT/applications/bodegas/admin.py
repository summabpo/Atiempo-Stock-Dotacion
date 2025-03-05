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

    # Excluir los campos 'fecha_creacion' y 'fecha_edicion' ya que no son editables
    exclude = ('fecha_creacion', 'fecha_edicion')

    # Opcionalmente, puedes hacer que los campos se muestren en un solo formulario de edición
    fieldsets = (
        (None, {
            'fields': ('nombre', 'direccion', 'id_ciudad', 'estado')
        }),
        ('Usuario', {
            'fields': ('id_usuario_creador', 'id_usuario_editor')
        }),
        # 'fecha_creacion' y 'fecha_edicion' no se deben mostrar en este formulario
    )

# Registrar el modelo 'Bodega' con la clase de configuración 'BodegaAdmin'
admin.site.register(Bodega, BodegaAdmin)