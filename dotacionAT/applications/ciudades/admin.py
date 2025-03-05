from django.contrib import admin
from .models import Ciudad

@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display = ('id_ciudad', 'nombre', 'fecha_creacion', 'activo', 'id_usuario_insert')
    list_filter = ('activo',)
    search_fields = ('nombre',)

