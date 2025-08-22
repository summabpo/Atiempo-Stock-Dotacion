from django import forms

import re
from datetime import datetime

class CargarArchivoForm(forms.Form):
    archivo = forms.FileField(
        label="Seleccione el archivo Excel o TXT"
    )
    periodo = forms.CharField(
        label="Periodo",
        required=False,
        max_length=7,  # Formato MM/YYYY
        widget=forms.TextInput(attrs={'placeholder': 'MM/YYYY'})
    )
    tipo_entrega = forms.ChoiceField(
        label="Tipo de Entrega",
        required=True,
        choices=[
            ('', 'Seleccione...'),
            ('ingreso', 'Ingreso'),
            ('ley', 'Por Ley')
        ],
        widget=forms.Select()
    )

 