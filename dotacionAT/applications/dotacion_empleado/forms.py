from django import forms

class CargarArchivoForm(forms.Form):
    archivo = forms.FileField(label="Seleccione el archivo Excel o TXT")