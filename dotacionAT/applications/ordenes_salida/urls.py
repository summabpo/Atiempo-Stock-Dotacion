from django.urls import path
from . import views

urlpatterns = [
    path('ordenes_salida/', views.ordenes_salida, name='ordenes_salida'),  # Aquí debe estar 'productos'
    path('list_orden_salida/', views.list_orden_salida, name='list_orden_salida'),  # Aquí debe estar 'productos'
    path('crear_salida/', views.crear_salida, name='crear_salida'),
    path('detalle_salida/<int:id>/', views.detalle_salida, name='detalle_salida'),


]