from django import forms
from .models import Ciudad

class CiudadNueva(forms.ModelForm):
    
    class Meta:
        nombre = forms.CharField(label="Ciudad", required=True, max_length=200, widget=forms.TextInput(attrs={'class': 'input'}))
        model = Ciudad
        fields = ['nombre']