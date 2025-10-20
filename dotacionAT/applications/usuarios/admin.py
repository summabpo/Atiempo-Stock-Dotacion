from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Usuario
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'rol', 'estado')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined', 'fecha_creacion')}),
    )

    readonly_fields = ('fecha_creacion', 'date_joined', 'last_login')

    # 👇 Aquí mostramos el nombre completo calculado
    list_display = ('username', 'nombre_completo', 'email', 'rol', 'estado', 'sucursal', 'is_staff', 'is_active', 'date_joined')

    list_filter = ('rol', 'estado', 'sucursal', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')