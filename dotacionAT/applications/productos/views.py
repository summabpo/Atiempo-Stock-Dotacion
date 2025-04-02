from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto
from .forms import ProductoForm
from pathlib import Path
from django.contrib import messages


# Importar las categorías desde el archivo choices_categoria.py
from ..data.choices_categorias import CATEGORIAS

# Create your views here.

def productos(request):
    producto = Producto.objects.all()
    return render (request, 'productos.html', {
        'productos': producto
    })
    
def crear_productos(request):
    categorias_choices = [('', 'Seleccione una opcion')] + CATEGORIAS  # Preparar las opciones para el select
    if request.method == 'POST':
        form = ProductoForm(request.POST, categorias_choices=categorias_choices)  # Pasamos las categorías al formulario
        if form.is_valid():
            form.save()  # Guardar el producto
            messages.success(request, "Producto Actualizada Correctamente. ! ")
            return redirect('productos')  # Redirigir después de guardar
    else:
        form = ProductoForm(categorias_choices=categorias_choices)  # Pasar las categorías al formulario

    return render(request, 'crear_productos.html', {'form': form})



def productos_detalle(request, id):
    ##ciudad = Ciudad.objects.get(id_ciudad=id)
    productos =  get_object_or_404(Producto, id_producto=id)
    print(productos)
    return render(request, 'productosDetalle.html',
                  {
                      'productos':productos
                  })    
    

def modificar_producto(request, id):
    producto = get_object_or_404(Producto, id_producto=id)

    # Preparar las opciones para el select (de la misma forma que en crear_productos)
    categorias_choices = [('', 'Seleccione una opción')] + CATEGORIAS

    # Datos iniciales para el formulario
    data = {
        'form': ProductoForm(instance=producto, categorias_choices=categorias_choices)
    }

    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST, instance=producto, categorias_choices=categorias_choices)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Producto Actualizada Correctamente. ! ")
            return redirect(to='productos')  # Redirigir después de guardar
        data['form'] = formulario

    return render(request, 'editarProducto.html', data)