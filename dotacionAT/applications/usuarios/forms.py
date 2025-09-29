from django import forms
from django.core.exceptions import ValidationError
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese contraseña'}),
        required=False  # lo controlamos en __init__
    )

    nombre_completo = forms.CharField(
        label="Nombre completo",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'})
    )

    class Meta:
        model = Usuario
        fields = ['username', 'nombre_completo', 'rol', 'estado', 'email', 'sucursal', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario o CC'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'sucursal': forms.Select(attrs={'class': 'form-control'}),  # 👈 select con bodegas
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
      
        if self.instance and self.instance.pk:  # edición
            self.fields['username'].widget.attrs['readonly'] = True
            self.fields['password'].required = False
            self.fields['password'].widget.attrs['placeholder'] = "Dejar en blanco para mantener la actual"
            self.fields['password'].help_text = "Si no escribes nada, la contraseña no cambiará."
            
            if self.instance:
                self.fields['sucursal'].initial = self.instance.sucursal
            
        else:  # creación
            self.fields['password'].required = True

        if self.instance and self.instance.pk:
            self.fields['nombre_completo'].initial = f"{self.instance.first_name} {self.instance.last_name}".strip()

        for name, field in self.fields.items():
            if name != "password":
                field.required = True

        self.fields['rol'].choices = [("", "Seleccione un rol")] + list(self.fields['rol'].choices)
        self.fields['estado'].choices = [("", "Seleccione un estado")] + list(self.fields['estado'].choices)

    def save(self, commit=True):
        # Guardar el hash original ANTES de que lo pise el super()
        current_password = None
        if self.instance and self.instance.pk:
            current_password = Usuario.objects.get(pk=self.instance.pk).password  

        user = super().save(commit=False)

        # Guardar nombre completo dividiéndolo en first_name y last_name
        nombre_completo = self.cleaned_data.get("nombre_completo", "").strip()
        if nombre_completo:
            partes = nombre_completo.split(" ", 1)
            user.first_name = partes[0]
            user.last_name = partes[1] if len(partes) > 1 else ""

        password = self.cleaned_data.get("password")

        if password:  
            # Nueva contraseña → encriptar
            user.set_password(password)
        else:
            # Mantener la contraseña vieja si no cambiaron nada
            if current_password:
                user.password = current_password

        if commit:
            user.save()
        return user