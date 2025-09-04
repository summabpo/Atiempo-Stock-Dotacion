from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from .models import GrupoDotacion, GrupoDotacionProducto, Cargo
from applications.productos.models import Producto, Categoria
from applications.clientes.models import Cliente
from applications.ciudades.models import Ciudad

# -------------------------------
# Formulario para GrupoDotacion
# -------------------------------

class GrupoDotacionForm(forms.ModelForm):
    class Meta:
        model = GrupoDotacion
        fields = ['cargos', 'cliente', 'ciudades', 'genero']
        widgets = {
            'cargos': forms.SelectMultiple(attrs={'class': 'select2'}),
            'ciudades': forms.SelectMultiple(attrs={'class': 'select2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.filter(activo=True).order_by('nombre')
        self.fields['cargos'].queryset = Cargo.objects.filter(activo=True).order_by('nombre')
        self.fields['ciudades'].queryset = Ciudad.objects.all().order_by('nombre')

# -------------------------------
# Formulario para GrupoDotacionProducto
# (ahora usando Categoría)
# -------------------------------

class GrupoDotacionProductoForm(forms.ModelForm):
    class Meta:
        model = GrupoDotacionProducto
        fields = ['categoria', 'cantidad']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = Categoria.objects.filter(activo=True).order_by('nombre')
        self.fields['categoria'].widget.attrs.update({'class': 'select2'})  # opcional si usas Select2

# -------------------------------
# Validación para evitar categorías repetidas
# -------------------------------

class BaseGrupoDotacionProductoFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        categorias = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                categoria = form.cleaned_data.get('categoria')
                if categoria in categorias:
                    raise forms.ValidationError("No puedes agregar categorías repetidas.")
                categorias.append(categoria)

# -------------------------------
# Formset Inline
# -------------------------------

GrupoDotacionProductoFormSet = inlineformset_factory(
    GrupoDotacion,
    GrupoDotacionProducto,
    form=GrupoDotacionProductoForm,
    formset=BaseGrupoDotacionProductoFormSet,
    fields=['categoria', 'cantidad'],
    extra=1,
)