from django.urls import path 
from . import views

urlpatterns = [
    path('bodegas/', views.bodegas, name='bodegas'),
    path('crear_bodega', views.crear_bodega, name='crear_bodega'),
    path('bodega/<int:id>/', views.bodega_detalle, name='bodega_detalle'),
    path('modificar_bodega/<int:id>/', views.modificar_bodega, name='modificar_bodega'),  # Aquí debe estar 'productos'
    
]