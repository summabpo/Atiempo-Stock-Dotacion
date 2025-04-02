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
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria']  # Los campos que deseas permitir editar

    categoria = forms.ChoiceField(choices=[], required=True)  # Inicializar con opciones vacías

    def __init__(self, *args, categorias_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Si se pasaron categorías, las asignamos al campo 'categoria'
        if categorias_choices:
            self.fields['categoria'].choices = categorias_choices