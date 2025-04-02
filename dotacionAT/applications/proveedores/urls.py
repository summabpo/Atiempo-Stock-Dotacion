from django.urls import path
from . import views

urlpatterns = [
    path('proveedor/', views.proveedor, name='proveedores'),  # Cambiado a proveedor
    path('crear_proveedor/', views.crear_proveedor, name='crear_proveedor'),
    path('proveedor/<int:id>', views.proveedor_detalle, name='proveedor_detalle'),
    path('modificar_proveedor/<int:id>/', views.modificar_proveedor, name='modificar_proveedor'),
]