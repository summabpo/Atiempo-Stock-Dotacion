
from django import forms
from .models import Cliente
from applications.ciudades.models import Ciudad  # Si es necesario, importar la clase de Ciudad
from django_select2.forms import Select2Widget

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'ciudad', 'telefono', 'email', 'direccion']  # Campos que quieras mostrar en el formulario
        widgets = {
            'nombre': forms.TextInput(attrs={'rows': 3, 'placeholder': 'Nombre Cliente'}),
            'direccion': forms.TextInput(attrs={'rows': 3, 'placeholder': 'Ingrese la dirección aquí...'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Número de teléfono'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}),
            'ciudad': Select2Widget(attrs={'class': 'form-control text-black', 'data-placeholder': 'Selecciona una ciudad'}),
        }

    # Si deseas hacer validaciones personalizadas, puedes hacerlo aquí
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and not telefono.isdigit():
            raise forms.ValidationError("El número de teléfono solo debe contener dígitos.")
        return telefono

    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     if email and not email.endswith('@gmail.com'):  # Un ejemplo de validación
    #         raise forms.ValidationError("Solo se permite el dominio '@gmail.com'.")
    #     return email
    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if '@' not in correo:
            raise forms.ValidationError("El correo debe contener un '@'.")
        return correo
    
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ciudad'].queryset = Ciudad.objects.all()
        self.fields['ciudad'].label = "Ciudad"