from django.contrib import admin
from .models import EmpleadoDotacion


# Register your models here.

@admin.register(EmpleadoDotacion)
class EmpleadoDotacionAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombre', 'cliente', 'fecha_ingreso', 'fecha_registro')
    search_fields = ('cedula', 'nombre', 'cliente')