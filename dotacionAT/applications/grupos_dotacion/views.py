from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
from .models import GrupoDotacion, GrupoDotacionProducto
from .forms import GrupoDotacionForm, GrupoDotacionProductoFormSet 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.

# @login_required
# def listar_grupos_dotacion(request):
#     grupos = GrupoDotacion.objects.all().select_related('cargo', 'cliente', 'ciudad')
#     return render(request, 'lista_grupos.html', {'grupos': grupos})

@login_required
def listar_grupos_dotacion(request):
    grupos = GrupoDotacion.objects.all() \
        .select_related('cliente', 'creado_por') \
        .prefetch_related('cargos', 'ciudades', 'categorias__categoria')
    return render(request, 'lista_grupos.html', {'grupos': grupos})



@login_required
def crear_grupo_dotacion(request):
    if request.method == 'POST':
        form = GrupoDotacionForm(request.POST)
        formset = GrupoDotacionProductoFormSet(request.POST, prefix='productos')

        if form.is_valid() and formset.is_valid():
            grupo = form.save(commit=False)
            grupo.creado_por = request.user
            grupo.save()

            form.save_m2m()  # ← ESTO ES CLAVE para guardar ManyToMany como cargos y ciudades

            formset.instance = grupo
            formset.save()

            return redirect('listar_grupos_dotacion')
    else:
        form = GrupoDotacionForm()
        formset = GrupoDotacionProductoFormSet(prefix='productos')

    return render(request, 'crear_grupo.html', {
        'form': form,
        'formset': formset,
    })