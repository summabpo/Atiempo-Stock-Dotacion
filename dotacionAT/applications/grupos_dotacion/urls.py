from django.urls import path, include
from . import views


urlpatterns = [
    path('crear-grupo/', views.crear_grupo_dotacion, name='crear_grupo_dotacion'),
    path('listar-grupos/', views.listar_grupos_dotacion, name='listar_grupos_dotacion'),
]
