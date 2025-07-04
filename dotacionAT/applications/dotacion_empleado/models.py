from django.db import models

# Create your models here.

class EmpleadoDotacion(models.Model):
    cedula = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=50)
    fecha_ingreso = models.DateField()
    cargo = models.CharField(max_length=100)
    cliente = models.CharField(max_length=100)
    centro_costo = models.CharField(max_length=100)
    sexo = models.CharField(max_length=20)

    talla_camisa = models.CharField(max_length=20, blank=True, null=True)
    cantidad_camisa = models.PositiveIntegerField(default=0, blank=True, null=True)

    talla_pantalon = models.CharField(max_length=20, blank=True, null=True)
    cantidad_pantalon = models.PositiveIntegerField(default=0, blank=True, null=True)

    talla_zapatos = models.CharField(max_length=20, blank=True, null=True)
    
    cantidad_zapatos = models.PositiveIntegerField(default=0, blank=True, null=True)

    cantidad_botas_caucho = models.PositiveIntegerField(default=0, blank=True, null=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nombre} ({self.cedula})'
    
    
    class Meta:
        verbose_name = "Empleado con Dotación"
        verbose_name_plural = "Empleados con Dotación"
        
    class Meta:
        ordering = ['-fecha_registro']    