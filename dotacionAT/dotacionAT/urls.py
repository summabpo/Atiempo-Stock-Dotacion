"""
URL configuration for dotacionAT project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
#from . import views
#from applications.ciudades import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('applications.ciudades.urls')),
    path('', include('applications.bodegas.urls')),
    path('', include('applications.proveedores.urls')),
    path('', include('applications.productos.urls')),
    path('', include('applications.ordenes_compra.urls')),
    path('', include('applications.inventario.urls')),  
    path('', include('applications.clientes.urls')),
    path('', include('applications.ordenes_salida.urls')),
    path('', include('applications.usuarios.urls')),
    path('select2/', include('django_select2.urls')),
    # path('add_venta/',views.add_ventas.as_view(), name='AddVenta'),
    # path('export/', views.export_pdf_view, name="ExportPDF" ),
    # path('export/<id>/<iva>', views.export_pdf_view, name="ExportPDF" )     
]

from django.conf import settings


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ] 

# urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)