from django.urls import path, include
from . import views

urlpatterns = [
    path('inventario_bodega_list/', views.inventario_bodega_list, name='inventario_bodega_list'),  # Aquí debe estar 'productos'
    path('inventario_bodega_json/', views.inventario_bodega_json, name='inventario_bodega_json'),
    path('cargar_inventario/', views.cargar_inventario, name='cargar_inventario'),
    path('registrar_inventario_inicial/', views.registrar_inventario_inicial, name='registrar_inventario_inicial'),
    path('', views.index, name='index'),  # ← ahora / mostrará el index  
]