# from django import forms
# from .models import Producto, Categoria

# class ProductoForm(forms.ModelForm):
#     class Meta:
#         model = Producto
#         fields = ['nombre', 'categoria', 'id_usuario']  # Los campos que deseas permitir editar

#     # Aquí puedes agregar validaciones adicionales o personalizar campos si es necesario
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Si quieres personalizar la forma en que se muestra el campo de categoría, por ejemplo:
#         self.fields['categoria'].queryset = Categoria.objects.all()  # Asegura que las categorías estén disponibles


from django import forms
from .models import Producto, Categoria
from ..data.choices import unidadMedida
from django_select2.forms import Select2Widget
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'unidad_medida']  # Los campos que deseas permitir editar

    categoria = forms.ModelChoiceField(queryset=Categoria.objects.all(), empty_label="Seleccione una categoría", required=False)
    widgets = {
            'categoria': Select2Widget(attrs={'class': 'form-control text-black', 'data-placeholder': 'Selecciona una Categoria'}),
            'unidad_medida': Select2Widget(attrs={'class': 'form-control text-black', 'data-placeholder': 'Selecciona una Unidad'}),
        }

    def __init__(self, *args, categorias_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Si se pasaron categorías, las asignamos al campo 'categoria'
        
        
class ProductoFormEdit(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'unidad_medida', 'activo']  # Los campos que deseas permitir editar

    categoria = forms.ModelChoiceField(queryset=Categoria.objects.all(), empty_label="Seleccione una categoría", required=False)
    
    unidad_medida = forms.ChoiceField(choices=unidadMedida, required=False)

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