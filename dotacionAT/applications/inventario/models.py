from django.db import models
from django.utils import timezone
from applications.productos.models import Producto
from applications.bodegas.models import Bodega


# Create your models here.


class InventarioBodega(models.Model):
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

    entradas = models.PositiveIntegerField(default=0, verbose_name="Total de Entradas")
    salidas = models.PositiveIntegerField(default=0, verbose_name="Total de Salidas")
    stock = models.IntegerField(default=0, verbose_name="Stock Actual")

    ultima_entrada = models.DateTimeField(null=True, blank=True)
    ultima_salida = models.DateTimeField(null=True, blank=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('bodega', 'producto')
        verbose_name = 'Inventario por Bodega'
        verbose_name_plural = 'Inventarios por Bodega'
        ordering = ['bodega', 'producto']

    def __str__(self):
        return f"{self.bodega.nombre} - {self.producto.nombre}"

    def registrar_entrada(self, cantidad):
        if cantidad <= 0:
            raise ValueError("La cantidad de entrada debe ser mayor que 0.")
        self.entradas += cantidad
        self.stock += cantidad
        self.ultima_entrada = timezone.now()
        self.save()

    def registrar_salida(self, cantidad):
        if cantidad <= 0:
            raise ValueError("La cantidad de salida debe ser mayor que 0.")
        if cantidad > self.stock:
            raise ValueError("No hay suficiente stock disponible.")
        self.salidas += cantidad
        self.stock -= cantidad
        self.ultima_salida = timezone.now()
        self.save()

    @property
    def disponible(self):
        return self.stock

