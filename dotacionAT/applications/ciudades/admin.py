from django.contrib import admin
from .models import Ciudad
@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display = ('id_ciudad', 'nombre', 'fecha_creacion', 'activo', 'id_usuario_insert', 'id_usuario_update')
    list_filter = ('activo',)
    search_fields = ('nombre',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Si es un nuevo objeto, se guarda quien lo creó
            obj.id_usuario_insert = request.user
        else:
            # Si ya existe, se guarda quien lo modificó
            obj.id_usuario_update = request.user
        super().save_model(request, obj, form, change)