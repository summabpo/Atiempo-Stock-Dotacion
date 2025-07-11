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
        .select_related('cargo', 'cliente', 'ciudad') \
        .prefetch_related('productos__producto')  # Prefetch los productos y el producto asociado
    return render(request, 'lista_grupos.html', {'grupos': grupos})



@login_required
def crear_grupo_dotacion(request):
    if request.method == 'POST':
        form = GrupoDotacionForm(request.POST)
        formset = GrupoDotacionProductoFormSet(request.POST, prefix='productos')  # 👈 Usa el prefix igual que en el template

        if form.is_valid() and formset.is_valid():
            grupo = form.save(commit=False)
            grupo.creado_por = request.user
            grupo.save()

            formset.instance = grupo
            formset.save()

            return redirect('listar_grupos_dotacion')
    else:
        form = GrupoDotacionForm()
        formset = GrupoDotacionProductoFormSet(prefix='productos')  # 👈 Mismo prefix que en el template

    return render(request, 'crear_grupo.html', {
        'form': form,
        'formset': formset,
    })