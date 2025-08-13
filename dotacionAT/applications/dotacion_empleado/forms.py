from django import forms

import re
from datetime import datetime

class CargarArchivoForm(forms.Form):
    archivo = forms.FileField(label="Seleccione el archivo Excel o TXT")
    periodo = forms.CharField(
        label="Periodo",
        max_length=7,  # Formato MM/YYYY
        widget=forms.TextInput(attrs={'placeholder': 'MM/YYYY'})
    )

 