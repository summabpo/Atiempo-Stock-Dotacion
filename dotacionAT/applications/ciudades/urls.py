from django.urls import path, include 
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Esto corresponde a la vista 'index'
    path('hello/<str:username>', views.hello, name='hello'),
    path('ciudades/', views.ciudades, name='ciudades'),
    path('list_ciudades/', views.list_ciudades, name='list_ciudades'),
    path('ciudades/<int:id>', views.ciudad_detalle, name='ciudad_detalle'),
    path('ciudad/<int:id>', views.ciudad, name='ciudad'),
    path('crear_ciudad', views.crear_ciudad, name='crear_ciudad'),
    path('modificar_ciudad/<int:id>/', views.modificar_ciudad, name='modificar_ciudad'),  # Aquí debe estar 'productos'
]


# from django.conf import settings


# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += [
#         path('__debug__/', include(debug_toolbar.urls)),
#     ] 