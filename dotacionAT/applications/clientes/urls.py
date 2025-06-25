from django.urls import path, include
from . import views

urlpatterns = [
    path('cliente/', views.cliente, name='cliente'),  # Cambiado a proveedor
    path('list_clientes/', views.list_clientes, name='list_clientes'),
    path('crear_cliente/', views.crear_cliente, name='crear_cliente'),
    path('modificar_cliente/<int:id>/', views.modificar_cliente, name='modificar_cliente'),

  
]


# from django.conf import settings


# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += [
#         path('__debug__/', include(debug_toolbar.urls)),
#     ] 