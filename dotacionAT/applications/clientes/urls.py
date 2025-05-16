from django.urls import path
from . import views

urlpatterns = [
    path('cliente/', views.cliente, name='cliente'),  # Cambiado a proveedor
    path('list_clientes/', views.list_clientes, name='list_clientes'),
  
]