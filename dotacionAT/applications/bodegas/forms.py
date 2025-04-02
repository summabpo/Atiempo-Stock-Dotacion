# from django import forms
# from .models import Bodega

# class BodegaNueva(forms.ModelForm):
#      class Meta:
#         nombre = forms.CharField(label="Bodega", required=True, max_length=200, widget=forms.TextInput(attrs={'class': 'input'}))
#         model = Bodega
#         fields = ['nombre']


# from django import forms
# from .models import Bodega
#  # Importa el modelo Ciudad si no lo has hecho

# class BodegaNueva(forms.ModelForm):
#     class Meta:
#         model = Bodega
#         fields = ['nombre', 'id_ciudad', 'direccion', 'estado', 'id_usuario_creador', 'id_usuario_editor']
        
#         widgets = {
#             'nombre': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nombre de la Bodega'}),
#             'direccion': forms.Textarea(attrs={'class': 'input', 'placeholder': 'Dirección de la Bodega'}),
#             'estado': forms.Select(attrs={'class': 'input'}),
#             'id_ciudad': forms.Select(attrs={'class': 'input'}),
#             'id_usuario_creador': forms.Select(attrs={'class': 'input'}),
#             'id_usuario_editor': forms.Select(attrs={'class': 'input'}),
#         }
        
#     # Si quieres agregar alguna validación adicional, puedes hacerlo aquí.
#     def clean_estado(self):
#         estado = self.cleaned_data.get('estado')
#         if estado not in ['activo', 'inactivo']:
#             raise forms.ValidationError("Estado inválido")
#         return estado

from django import forms
from .models import Bodega, Ciudad
from django.contrib.auth import get_user_model

class BodegaNueva(forms.ModelForm):
    class Meta:
        model = Bodega
        fields = ['nombre', 'id_ciudad', 'direccion', 'estado']
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nombre de la Bodega'}),
            'direccion': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Dirección de la Bodega'}),
            'estado': forms.Select(attrs={'class': 'input'}),
            'id_ciudad': forms.Select(attrs={'class': 'input'}),
            'id_usuario_creador': forms.Select(attrs={'class': 'input'}),
            'id_usuario_editor': forms.Select(attrs={'class': 'input'}),
        }

    # Validación del estado
    def clean_estado(self):
        estado = self.cleaned_data.get('estado')
        if estado not in ['activo', 'inactivo']:
            raise forms.ValidationError("Estado inválido")
        return estado
    
    # Validación para asegurarse de que se seleccione una ciudad válida
    def clean_id_ciudad(self):
        id_ciudad = self.cleaned_data.get('id_ciudad')
        if not id_ciudad:
            raise forms.ValidationError("Debe seleccionar una ciudad.")
        return id_ciudad

    # Cargar las ciudades en el campo id_ciudad
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asigna a 'id_ciudad' todas las ciudades de la base de datos
        self.fields['id_ciudad'].queryset = Ciudad.objects.all()
        # self.fields['id_usuario_creador'].queryset = get_user_model().objects.all()  # Asegura que los usuarios estén disponibles
        # self.fields['id_usuario_editor'].queryset = get_user_model().objects.all()  # Lo mismo para id_usuario_editor