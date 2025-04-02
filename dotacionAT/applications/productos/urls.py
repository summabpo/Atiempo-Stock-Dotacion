from django.urls import path
from . import views

urlpatterns = [
    path('productos/', views.productos, name='productos'),  # Aquí debe estar 'productos'
    path('crear_productos/', views.crear_productos, name='crear_productos'),  # Aquí debe estar 'productos'
    path('productos_detalle/<int:id>/', views.productos_detalle, name='productos_detalle'),  # Aquí debe estar 'productos'
    path('modificar_producto/<int:id>/', views.modificar_producto, name='modificar_producto'),  # Aquí debe estar 'productos'
    

]