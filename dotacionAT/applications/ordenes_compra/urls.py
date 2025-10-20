from django.urls import path, include
from . import views

urlpatterns = [
    path('ordenes_compra/', views.ordenes_compra, name='ordenes_compra'),  # Aquí debe estar 'productos'
    path('crear_orden_compra/', views.crear_orden_compra, name='crear_orden_compra'),
    path('comprar_orden/<int:id>/', views.comprar_orden, name='comprar_orden'),  # Aquí debe estar 'productos'
    path('detalle_comprar/<int:id>/', views.detalle_comprar, name='detalle_comprar'),  # Aquí debe estar 'productos'    
    path('list_orden_y_compra/', views.list_orden_y_compra, name='list_orden_y_compra'),  # Aquí debe estar 'productos'
    path('cambiar_estado_orden/<int:orden_id>/', views.cambiar_estado_orden, name='cambiar_estado_orden'),
]