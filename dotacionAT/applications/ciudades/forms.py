from django import forms
from .models import Ciudad

class CiudadNueva(forms.ModelForm):
    
    class Meta:
        nombre = forms.CharField(label="Ciudad", required=True, max_length=200, widget=forms.TextInput(attrs={'class': 'input'}))
        model = Ciudad
        fields = ['nombre']
        
        
class CiudadActualizaForm(forms.ModelForm):
    class Meta:
        model = Ciudad
        fields = ['nombre', 'activo']  # Especifica los campos que deseas permitir

    # Aquí puedes agregar validaciones o personalizaciones específicas para la actualización
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalización para actualizar
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})
        self.fields['activo'].widget.attrs.update({'class': 'form-control'})        
        