from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Categoria
from django.http import JsonResponse
from .forms import ProductoForm, CategoriaNueva, CategoriaEditar, ProductoFormEdit
from pathlib import Path
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.html import escape
import unicodedata


# Importar las categorías desde el archivo choices_categoria.py
from ..data.choices import CATEGORIAS

# Create your views here.

def normalizar_nombre_producto(nombre):
    nombre = unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('utf-8')
    nombre = nombre.lower().strip().replace(" ", "")
    return nombre

def normalizar_nombre_categoria(nombre):
    # 1. Quitar tildes
    nombre = unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('utf-8')
    # 2. Convertir a minúsculas y eliminar espacios
    nombre = nombre.lower().strip().replace(" ", "")
    # 3. Convertir a singular (regla básica)
    if nombre.endswith('s') and not nombre.endswith('es'):
        nombre = nombre[:-1]
    return nombre


@login_required(login_url='login_usuario')
def list_productos(_request):
    # productos =list(Producto.objects.values())
    # data={'productos':productos}
    # return JsonResponse(data)
    productos = Producto.objects.all()
    data = {
        'productos': [
            {
                'id_producto': producto.id_producto,
                'nombre': producto.nombre,
                'categoria': producto.categoria.nombre,
                'unidad_medida': producto.unidad_medida,
                'stock': producto.stock,
                'costo': producto.costo,
                'activo': producto.activo,
                'url_editar': reverse('modificar_producto', args=[producto.id_producto])
            } for producto in productos
        ]
    }
    return JsonResponse(data)

@login_required(login_url='login_usuario')
def productos(request):
    producto = Producto.objects.all()
    return render (request, 'productos.html', {
        'productos': producto
    })
    

@login_required(login_url='login_usuario')
def crear_productos(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            nombre_ingresado = form.cleaned_data['nombre']
            nombre_normalizado = normalizar_nombre_producto(nombre_ingresado)

            for p in Producto.objects.all():
                if normalizar_nombre_producto(p.nombre) == nombre_normalizado:
                    messages.error(
                        request,
                        f"⚠️ El producto {escape(nombre_ingresado)} ya está registrado como {p.nombre}."
                    )
                    return render(request, 'crear_productos.html', {'form': form})

            producto = form.save(commit=False)
            producto.id_usuario = request.user
            producto.save()
            messages.success(request, "Producto creado correctamente.")
            return redirect('productos')
    else:
        form = ProductoForm()

    return render(request, 'crear_productos.html', {'form': form})



@login_required(login_url='login_usuario')
def productos_detalle(request, id):
    ##ciudad = Ciudad.objects.get(id_ciudad=id)
    productos =  get_object_or_404(Producto, id_producto=id)
    print(productos)
    return render(request, 'productosDetalle.html',
                  {
                      'productos':productos
                  })    
    
@login_required(login_url='login_usuario')
def modificar_producto(request, id):
    producto = get_object_or_404(Producto, id_producto=id)

    data = {
        'form': ProductoFormEdit(instance=producto)
    }

    if request.method == 'POST':
        formulario = ProductoFormEdit(data=request.POST, instance=producto)
        if formulario.is_valid():
            producto_actualizado = formulario.save(commit=False)
            producto_actualizado.usuario_edita = request.user  # ← Guardar editor
            producto_actualizado.save()
            messages.success(request, "Producto actualizado correctamente.")
            return redirect('productos')
        data['form'] = formulario

    return render(request, 'editarProducto.html', data)

@login_required(login_url='login_usuario')
def categorias(request):
    categoria = Categoria.objects.all()
    return render (request, 'categorias.html', {
        'categorias': categoria
    })

@login_required(login_url='login_usuario')
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
    
    


@login_required(login_url='login_usuario')
def crear_categoria(request):
    if request.method == 'GET':
        return render(request, 'crear_categoria.html', {
            'form': CategoriaNueva()
        })
    else:
        nombre = request.POST['nombre'].strip().title()
        nombre_normalizado = normalizar_nombre_categoria(nombre)

        # Comparamos con todas las categorías existentes
        categorias = Categoria.objects.all()
        for c in categorias:
            if normalizar_nombre_categoria(c.nombre) == nombre_normalizado:
                messages.error(request, f"La categoría  {escape(nombre)}  ya existe como  {c.nombre} .")
                return render(request, 'crear_categoria.html', {
                    'form': CategoriaNueva(request.POST)
                })

        categoria = Categoria(
            nombre=nombre,
            id_usuario_creador=request.user
        )
        categoria.save()
        messages.success(request, "¡Categoría creada correctamente!")
        return redirect('categorias')

    
@login_required(login_url='login_usuario')
def modificar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id_categoria=id)
    data = {
        'form': CategoriaEditar(instance=categoria)
    }

    if request.method == 'POST':
        formulario = CategoriaEditar(data=request.POST, instance=categoria)
        if formulario.is_valid():
            categoria_actualizada = formulario.save(commit=False)
            categoria_actualizada.id_usuario_editor = request.user  # ← guardar quién edita
            categoria_actualizada.save()
            messages.success(request, "Categoría Actualizada Correctamente. ! ")
            return redirect('categorias')
        data['form'] = formulario

    return render(request, 'editarCategoria.html', data)    