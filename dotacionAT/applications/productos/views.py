from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Categoria
from django.http import JsonResponse
from .forms import ProductoForm, CategoriaNueva, CategoriaEditar, ProductoFormEdit
from pathlib import Path
from django.urls import reverse
from django.contrib import messages


# Importar las categorías desde el archivo choices_categoria.py
from ..data.choices import CATEGORIAS

# Create your views here.

def list_productos(_request):
    productos =list(Producto.objects.values())
    data={'productos':productos}
    return JsonResponse(data)
    # categorias = Producto.objects.all()
    # data = {
    #     'categorias': [
    #         {
    #             'id_categoria': categoria.id_categoria,
    #             'nombre': categoria.nombre,
    #             'activo': categoria.activo,
    #             'url_editar': reverse('modificar_categoria', args=[categoria.id_categoria])
    #         } for categoria in categorias
    #     ]
    # }
    # return JsonResponse(data)


def productos(request):
    producto = Producto.objects.all()
    return render (request, 'productos.html', {
        'productos': producto
    })
    
# def crear_productos(request):
#     categorias_choices = [('', 'Seleccione una opcion')] + CATEGORIAS  # Preparar las opciones para el select
#     if request.method == 'POST':
#         form = ProductoForm(request.POST, categorias_choices=categorias_choices)  # Pasamos las categorías al formulario
#         if form.is_valid():
#             form.save()  # Guardar el producto
#             messages.success(request, "Producto Actualizada Correctamente. ! ")
#             return redirect('productos')  # Redirigir después de guardar
#     else:
#         form = ProductoForm(categorias_choices=categorias_choices)  # Pasar las categorías al formulario

#     return render(request, 'crear_productos.html', {'form': form})

def crear_productos(request):
     
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()  # Guardar el producto
            messages.success(request, "Producto actualizado correctamente.")
            return redirect('productos')  # Redirigir después de guardar
    else:
        form = ProductoForm()

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
        'form': ProductoFormEdit(instance=producto)
    }

    if request.method == 'POST':
        formulario = ProductoFormEdit(data=request.POST, instance=producto)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Producto Actualizada Correctamente. ! ")
            return redirect(to='productos')  # Redirigir después de guardar
        data['form'] = formulario

    return render(request, 'editarProducto.html', data)


def categorias(request):
    categoria = Categoria.objects.all()
    return render (request, 'categorias.html', {
        'categorias': categoria
    })


def list_categorias(_request):
    # categorias =list(Categoria.objects.values())
    # data={'categorias':categorias}
    # return JsonResponse(data)
    categorias = Categoria.objects.all()
    data = {
        'categorias': [
            {
                'id_categoria': categoria.id_categoria,
                'nombre': categoria.nombre,
                'activo': categoria.activo,
                'url_editar': reverse('modificar_categoria', args=[categoria.id_categoria])
            } for categoria in categorias
        ]
    }
    return JsonResponse(data)
    
    
# def crear_categoria(request):
    
#     if request.method == 'POST':
#         form = ProductoForm(request.POST)  # Pasamos las categorías al formulario
#         if form.is_valid():
#             form.save()  # Guardar el producto
#             messages.success(request, "Categoria Creada Correctamente. ! ")
#             return redirect('categoria')  # Redirigir después de guardar
#     else:
#         form = ProductoForm(categorias_choices=categorias_choices)  # Pasar las categorías al formulario

#     return render(request, 'crear_productos.html', {'form': form})    


def crear_categoria(request):
    if request.method == 'GET':
        # show interface
        return render(request, 'crear_categoria.html', {
                      'form': CategoriaNueva()
        })
    else:
        Categoria.objects.create(nombre=request.POST['nombre'])
        messages.success(request, "Categoria Creada Correctamente. ! ")
        return redirect('categorias')
    
def modificar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id_categoria=id)

    # Preparar las opciones para el select (de la misma forma que en crear_productos)

    # Datos iniciales para el formulario
    data = {
        'form': CategoriaEditar(instance=categoria)
    }

    if request.method == 'POST':
        formulario = CategoriaEditar(data=request.POST, instance=categoria)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Categoria Actualizada Correctamente. ! ")
            return redirect(to='categorias')  # Redirigir después de guardar
        data['form'] = formulario

    return render(request, 'editarCategoria.html', data)    