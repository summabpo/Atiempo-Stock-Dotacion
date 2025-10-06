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
        choices=[],  # Se define en __init__
        widget=forms.Select()
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)  # recuperamos el usuario desde la view
        super().__init__(*args, **kwargs)

        # Opciones completas
        choices = [
            ('', 'Seleccione...'),
            ('ingreso', 'Ingreso'),
            ('ley', 'Por Ley'),
        ]

        # Si el usuario es de rol "almacen", restringimos
        if user and getattr(user, "rol", "").strip().lower() == "almacen":
            self.fields['tipo_entrega'].choices = [
                ('', 'Seleccione...'),
                ('ingreso', 'Ingreso'),
            ]
        else:
            self.fields['tipo_entrega'].choices = choices