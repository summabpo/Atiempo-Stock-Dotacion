from django.contrib import admin
from .models import Cliente
# Register your models here.

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    # Especifica los campos que aparecerán en la lista de clientes
    list_display = ('id_cliente', 'nombre', 'telefono', 'email', 'fecha_creacion', 'fecha_actualizacion', 'usuario_creador', 'usuario_editor', 'ciudad', 'activo')

    # Especifica los campos por los cuales se puede buscar
    search_fields = ('nombre', 'direccion', 'ciudad__nombre', 'telefono', 'email' , 'activo')  # Ahora puedes buscar por el nombre de la ciudad también

    # Especifica los filtros disponibles en el panel de administración
    list_filter = ('ciudad__nombre', 'fecha_creacion')  # Filtrar por ciudad y fecha de creación

    # Excluir los campos 'fecha_creacion' y 'fecha_edicion' ya que no son editables
    exclude = ('fecha_creacion', 'fecha_edicion')

    # Opcionalmente, puedes hacer que los campos se muestren en un solo formulario de edición
    fieldsets = (
        (None, {
            'fields': ('nombre', 'direccion', 'ciudad', 'telefono', 'email', 'activo')
        }),
        ('Usuario', {
            'fields': ('usuario_creador',)
        }),
        # 'fecha_creacion' y 'fecha_edicion' no se deben mostrar en este formulario
    )