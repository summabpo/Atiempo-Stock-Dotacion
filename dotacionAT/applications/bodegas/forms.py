from django import forms
from .models import Bodega, Ciudad
from django_select2.forms import Select2Widget

class BodegaNueva(forms.ModelForm):
    class Meta:
        model = Bodega
        fields = ['nombre', 'id_ciudad', 'direccion', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nombre de la Bodega'}),
            'direccion': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Dirección de la Bodega'}),
            'id_ciudad': Select2Widget(attrs={'class': 'form-control text-black', 'data-placeholder': 'Selecciona una ciudad'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_ciudad'].queryset = Ciudad.objects.all()
        self.fields['id_ciudad'].label = "Ciudad"