from django.urls import path
from . import views

urlpatterns = [
    path('inventario_bodega_list/', views.inventario_bodega_list, name='inventario_bodega_list'),  # Aquí debe estar 'productos'
    path('inventario_bodega_json/', views.inventario_bodega_json, name='inventario_bodega_json'),
  
]