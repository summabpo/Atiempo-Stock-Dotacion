from django.urls import path, include
from . import views

urlpatterns = [
    path('productos/', views.productos, name='productos'),  # Aquí debe estar 'productos'
    path('categorias/', views.categorias, name='categorias'),  # Aquí debe estar 'productos'
    path('crear_productos/', views.crear_productos, name='crear_productos'),  # Aquí debe estar 'productos'
    path('productos_detalle/<int:id>/', views.productos_detalle, name='productos_detalle'),  # Aquí debe estar 'productos'
    path('modificar_producto/<int:id>/', views.modificar_producto, name='modificar_producto'),  # Aquí debe estar 'productos'
    path('crear_categoria/', views.crear_categoria, name='crear_categoria'),  # Aquí debe estar 'productos'
    path('modificar_categoria/<int:id>/', views.modificar_categoria, name='modificar_categoria'),  # Aquí debe estar 'productos'
    path('list_categorias/', views.list_categorias, name='list_categorias'),  # Aquí debe estar 'productos'
    path('list_productos/', views.list_productos, name='list_productos'),  # Aquí debe estar 'productos'
]