from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('rol', 'estado', 'fecha_creacion'),
        }),
    )
    readonly_fields = ('fecha_creacion',)
    list_display = ('username', 'email', 'rol', 'estado', 'is_staff')