from django.urls import path, include
from . import views

urlpatterns = [
    path('cargar-empleados/', views.cargar_empleados_desde_excel, name='cargar_empleados'),
    path('empleadodotacion/', views.empleadodotacion, name='empleadodotacion'),
    path('list_empleados/', views.list_empleados, name='list_empleados'),
    path('historial-entregas/', views.historial_entregas, name='historial_entregas'),
]


