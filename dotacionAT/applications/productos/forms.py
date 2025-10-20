from django import forms
from .models import Producto, Categoria
from ..data.choices import unidadMedida
from django_select2.forms import Select2Widget
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'unidad_medida']  # Los campos que deseas permitir editar
        widgets = {
            'categoria': Select2Widget(attrs={'class': 'form-control text-black', 'data-placeholder': 'Selecciona una Categoria'}),
            'unidad_medida': Select2Widget(attrs={'class': 'form-control text-black', 'data-placeholder': 'Selecciona una Unidad'}),
        }

     # categoria = forms.ModelChoiceField(queryset=Categoria.objects.all(), empty_label="Seleccione una categoría", required=False)

    def __init__(self, *args, categorias_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Si se pasaron categorías, las asignamos al campo 'categoria'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = Categoria.objects.all()
        self.fields['categoria'].label = "categoria"    
        
class ProductoFormEdit(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'unidad_medida', 'activo']  # Los campos que deseas permitir editar
        widgets = {
            'categoria': Select2Widget(attrs={'class': 'form-control text-black', 'data-placeholder': 'Selecciona una Categoria'}),
            'unidad_medida': Select2Widget(attrs={'class': 'form-control text-black', 'data-placeholder': 'Selecciona una Unidad'}),
        }

    # categoria = forms.ModelChoiceField(queryset=Categoria.objects.all(), empty_label="Seleccione una categoría", required=False)
    
    # unidad_medida = forms.ChoiceField(choices=unidadMedida, required=False)

    def __init__(self, *args, categorias_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Si se pasaron categorías, las asignamos al campo 'categoria'        
                           
class CategoriaNueva(forms.ModelForm):
    
    class Meta:
        nombre = forms.CharField(label="Categoria", required=True, max_length=200, widget=forms.TextInput(attrs={'class': 'input'}))
        model = Categoria
        fields = ['nombre']  
        
class CategoriaEditar(forms.ModelForm):
    
    class Meta:
        nombre = forms.CharField(label="Categoria", required=True, max_length=200, widget=forms.TextInput(attrs={'class': 'input'}))
        model = Categoria
        fields = ['nombre', 'activo']                    