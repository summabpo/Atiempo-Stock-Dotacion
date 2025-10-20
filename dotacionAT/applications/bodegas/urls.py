from django.urls import path, include 
from . import views

urlpatterns = [
    path('bodegas/', views.bodegas, name='bodegas'),
    path('crear_bodega', views.crear_bodega, name='crear_bodega'),
    path('bodega/<int:id>/', views.bodega_detalle, name='bodega_detalle'),
    path('modificar_bodega/<int:id>/', views.modificar_bodega, name='modificar_bodega'), 
    path('list_bodegas/', views.list_bodegas, name='list_bodegas'),
    path('list_bodegas_filtradas/', views.list_bodegas_filtradas, name='list_bodegas_filtradas'),
]