from django.urls import path, include
from . import views

urlpatterns = [
    path('cargar-empleados/', views.cargar_empleados_desde_excel, name='cargar_empleados'),
    path('empleadodotacion/', views.empleadodotacion, name='empleadodotacion'),
    path('list_empleados/', views.list_empleados, name='list_empleados'),
    path('historial-entregas/', views.historial_entregas, name='historial_entregas'),
     path('historial-entregas2/', views.historial_entregas2, name='historial_entregas2'),
    path('entregas/pdf/todas/', views.generar_formato_entrega_pdf, name='generar_formato_entrega_pdf'),
    path('consolidado/', views.vista_consolidado, name='vista_consolidado'),
    path('pdf/', views.generar_pdf_por_periodo, name='pdf_por_periodo'),
    path('entrega/pdf/<int:entrega_id>/', views.generar_pdf_por_entrega, name='generar_pdf_por_entrega'),
]


