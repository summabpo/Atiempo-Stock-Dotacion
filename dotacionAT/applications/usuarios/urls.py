from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('login/', views.login_usuario, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('usuario/', views.usuario, name='usuario'),  # Cambiado a proveedor
    path('list_usuarios/', views.list_usuarios, name='list_usuarios'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path("editar/<int:user_id>/", views.editar_usuario, name="editar_usuario"),
]




    
