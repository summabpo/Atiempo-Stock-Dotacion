from django import forms
from .models import Ciudad
from .utils import normalizar_ciudad  # o desde donde hayas puesto la función

# class CiudadNueva(forms.ModelForm):
    
#     class Meta:
#         nombre = forms.CharField(label="Ciudad", required=True, max_length=200, widget=forms.TextInput(attrs={'class': 'input'}))
#         model = Ciudad
#         fields = ['nombre']

class CiudadNueva(forms.ModelForm):
    class Meta:
        model = Ciudad
        fields = ['nombre']

    def clean_nombre(self):
        nombre_ingresado = self.cleaned_data['nombre']
        nombre_normalizado = normalizar_ciudad(nombre_ingresado)

        # Verificar si ya existe una ciudad con ese nombre normalizado
        if Ciudad.objects.filter(nombre__iexact=nombre_normalizado).exists():
            raise forms.ValidationError(f"La ciudad '{nombre_normalizado}' ya está registrada.")
        
        return nombre_normalizado
        
        
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
        