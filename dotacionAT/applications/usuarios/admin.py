from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Personaliza la vista del admin para tu modelo de usuario
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('rol', 'estado', 'fecha_creacion', 'fecha_ultimo_login')}),
    )
    list_display = ('username', 'email', 'rol', 'estado', 'is_staff')