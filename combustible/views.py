from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CatalogoCliente, Transporte
from .forms import CatalogoClienteForm, TransporteForm


@login_required
def dashboard(request):
    return render(request, 'combustible/dashboard.html')


# Vistas para Catálogo de Cliente
@login_required
def lista_clientes(request):
    clientes = CatalogoCliente.objects.all()
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


# Vistas para Transporte
@login_required
def lista_transporte(request):
    transportes = Transporte.objects.all()
    return render(request, 'combustible/lista_transporte.html', {'transportes': transportes})


@login_required
def crear_vehiculo(request):
    if request.method == 'POST':
        form = TransporteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehículo agregado correctamente.')
            return redirect('lista_transporte')
        else:
            messages.error(request, 'Por favor, corrija los errores señalados.')
    else:
        form = TransporteForm()

    return render(request, 'combustible/crear_vehiculo.html', {'form': form})


@login_required
def editar_vehiculo(request, pk):
    vehiculo = get_object_or_404(Transporte, pk=pk)
    if request.method == 'POST':
        form = TransporteForm(request.POST, instance=vehiculo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehículo modificado correctamente.')
            return redirect('lista_transporte')
        else:
            messages.error(request, 'Por favor, corrija los errores señalados.')
    else:
        form = TransporteForm(instance=vehiculo)

    return render(request, 'combustible/editar_vehiculo.html', {'form': form, 'vehiculo': vehiculo})