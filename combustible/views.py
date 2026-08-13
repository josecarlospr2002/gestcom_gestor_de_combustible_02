from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CatalogoCliente
from .forms import CatalogoClienteForm


@login_required
def dashboard(request):
    return render(request, 'combustible/dashboard.html')


@login_required
def lista_clientes(request):
    clientes = CatalogoCliente.objects.all()

    # Filtros
    cliente = request.GET.get('cliente', '')
    clasificacion = request.GET.get('clasificacion', '')

    if cliente:
        clientes = clientes.filter(cliente__icontains=cliente)
    if clasificacion:
        clientes = clientes.filter(clasificacion=clasificacion)

    return render(request, 'combustible/lista_clientes.html', {'clientes': clientes})


@login_required
def crear_cliente(request):
    if request.method == 'POST':
        form = CatalogoClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente agregado correctamente.')
            return redirect('lista_clientes')
        else:
            messages.error(request, 'Por favor, corrija los errores señalados.')
    else:
        form = CatalogoClienteForm()

    return render(request, 'combustible/crear_cliente.html', {'form': form})


@login_required
def editar_cliente(request, pk):
    cliente = get_object_or_404(CatalogoCliente, pk=pk)
    if request.method == 'POST':
        form = CatalogoClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente modificado correctamente.')
            return redirect('lista_clientes')
        else:
            messages.error(request, 'Por favor, corrija los errores señalados.')
    else:
        form = CatalogoClienteForm(instance=cliente)

    return render(request, 'combustible/editar_cliente.html', {'form': form, 'cliente': cliente})


@login_required
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(CatalogoCliente, pk=pk)
    cliente.delete()
    messages.success(request, 'Cliente eliminado correctamente.')
    return redirect('lista_clientes')