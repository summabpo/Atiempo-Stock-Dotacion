from django.urls import path
from . import views

urlpatterns = [
    path('ordenes_compra/', views.ordenes_compra, name='ordenes_compra'),  # Aquí debe estar 'productos'
    # path('categorias/', views.categorias, name='categorias'),  # Aquí debe estar 'productos'
    path('crear_orden_compra/', views.crear_orden_compra, name='crear_orden_compra'),
    # path('productos_detalle/<int:id>/', views.productos_detalle, name='productos_detalle'),  # Aquí debe estar 'productos'
    path('comprar_orden/<int:id>/', views.comprar_orden, name='comprar_orden'),  # Aquí debe estar 'productos'
    # path('crear_categoria/', views.crear_categoria, name='crear_categoria'),  # Aquí debe estar 'productos'
    # path('modificar_categoria/<int:id>/', views.modificar_categoria, name='modificar_categoria'),  # Aquí debe estar 'productos'
    path('list_orden_compra/', views.list_orden_compra, name='list_orden_compra'),  # Aquí debe estar 'productos'
    # path('list_productos/', views.list_productos, name='list_productos'),  # Aquí debe estar 'productos'

]