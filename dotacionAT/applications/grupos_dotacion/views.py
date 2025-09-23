from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from .models import GrupoDotacion, GrupoDotacionProducto
from .forms import GrupoDotacionForm, GrupoDotacionProductoFormSet, GrupoDotacionProductoFormSetEdit 
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
        formset = GrupoDotacionProductoFormSet(request.POST, prefix='categorias')

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
        formset = GrupoDotacionProductoFormSet(prefix='categorias')

    return render(request, 'crear_grupo.html', {
        'form': form,
        'formset': formset,
    })
    
@login_required    
def editar_grupo_dotacion(request, pk):
    grupo = get_object_or_404(GrupoDotacion, pk=pk)

    if request.method == 'POST':
        form = GrupoDotacionForm(request.POST, instance=grupo)
        formset = GrupoDotacionProductoFormSetEdit(
            request.POST,
            instance=grupo,
            prefix='categorias'
        )

        if form.is_valid() and formset.is_valid():
            grupo = form.save()
            formset.save()  # Aquí ya guarda correctamente todas las categorías
            return redirect('listar_grupos_dotacion')
        else:
            print("Errores form:", form.errors)
            print("Errores formset:", formset.errors)
    else:
        form = GrupoDotacionForm(instance=grupo)
        formset = GrupoDotacionProductoFormSetEdit(instance=grupo, prefix='categorias')

    return render(request, 'editar-grupo.html', {
        'form': form,
        'formset': formset,
        'grupo': grupo
    })
    
    
@login_required 
def eliminar_grupo_dotacion(request, grupo_id):
    grupo = get_object_or_404(GrupoDotacion, id=grupo_id)
    
    if request.method == 'POST':
        grupo.delete()
        messages.success(request, 'Grupo de dotación eliminado correctamente.')
        return redirect('listar_grupos_dotacion')
    
    # Si es GET, mostrar confirmación (pero usaremos modal en el frontend)
    return redirect('listar_grupos_dotacion')
