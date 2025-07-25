# from django import forms
# from .models import GrupoDotacion, GrupoDotacionProducto
# from django.forms.models import inlineformset_factory, BaseInlineFormSet

# class GrupoDotacionForm(forms.ModelForm):
#     class Meta:
#         model = GrupoDotacion
#         fields = ['cargo', 'cliente', 'ciudad', 'genero']

# GrupoDotacionProductoFormSet = inlineformset_factory(
#     GrupoDotacion,
#     GrupoDotacionProducto,
#     fields=('producto', 'cantidad' ),
#     extra=1
# )

# class BaseGrupoDotacionProductoFormSet(BaseInlineFormSet):
#     def clean(self):
#         super().clean()
#         productos = []
#         for form in self.forms:
#             if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
#                 producto = form.cleaned_data.get('producto')
#                 if producto in productos:
#                     raise forms.ValidationError("No puedes agregar productos repetidos.")
#                 productos.append(producto)

# GrupoDotacionProductoFormSet = inlineformset_factory(
#     GrupoDotacion,
#     GrupoDotacionProducto,
#     fields=['producto', 'cantidad'],
#     extra=1,
#     can_delete=True,
#     formset=BaseGrupoDotacionProductoFormSet
# )

from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from .models import GrupoDotacion, GrupoDotacionProducto, Cargo
from applications.productos.models import Producto
from applications.clientes.models import Cliente
from applications.ciudades.models import Ciudad

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

class GrupoDotacionProductoForm(forms.ModelForm):
    class Meta:
        model = GrupoDotacionProducto
        fields = ['producto', 'cantidad']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 👇 Esta línea debería imprimirse si todo va bien
        print("Form cargando productos activos:", Producto.objects.filter(activo=True))
        self.fields['producto'].queryset = Producto.objects.filter(activo=True).order_by('nombre')

class BaseGrupoDotacionProductoFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        productos = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                producto = form.cleaned_data.get('producto')
                if producto in productos:
                    raise forms.ValidationError("No puedes agregar productos repetidos.")
                productos.append(producto)

GrupoDotacionProductoFormSet = inlineformset_factory(
    GrupoDotacion,
    GrupoDotacionProducto,
    form=GrupoDotacionProductoForm,  # 👈 Este debe apuntar al form que contiene el filtro
    formset=BaseGrupoDotacionProductoFormSet,
    fields=['producto', 'cantidad'],
    extra=1,
)