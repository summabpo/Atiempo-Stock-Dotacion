from django import forms
from .models import OrdenCompra

class OrdenCompraForm(forms.ModelForm):
    class Meta:
        model = OrdenCompra
        fields = ['proveedor']
        widgets = {
            'observaciones': forms.Textarea(attrs={'class': 'form-control'}),
            # 'proveedor': forms.Select(attrs={'class': 'form-control'}),
            # 'estado': forms.Select(attrs={'class': 'form-control'}),
        }