from django.urls import path, include
from . import views

urlpatterns = [
    path('inventario_bodega_list/', views.inventario_bodega_list, name='inventario_bodega_list'),  # Aquí debe estar 'productos'
    path('inventario_bodega_json/', views.inventario_bodega_json, name='inventario_bodega_json'),
    path('', views.index, name='index'),  # ← ahora / mostrará el index  
]


# from django.conf import settings


# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += [
#         path('__debug__/', include(debug_toolbar.urls)),
#     ] 