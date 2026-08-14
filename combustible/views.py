from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from .models import CatalogoCliente, Transporte, ModeloSolicitud, DetalleSolicitud, DetalleSolicitudVehiculo
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
    transportes = Transporte.objects.select_related('cliente').all()
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


@login_required
def eliminar_vehiculo(request, pk):
    vehiculo = get_object_or_404(Transporte, pk=pk)
    vehiculo.delete()
    messages.success(request, 'Vehículo eliminado correctamente.')
    return redirect('lista_transporte')


@login_required
def ver_cliente(request, pk):
    cliente = get_object_or_404(CatalogoCliente, pk=pk)
    vehiculos = Transporte.objects.filter(cliente=cliente)
    return render(request, 'combustible/ver_cliente.html', {
        'cliente': cliente,
        'vehiculos': vehiculos,
    })


# Vistas para Modelo de Solicitud
@login_required
def lista_solicitudes(request):
    solicitudes = ModeloSolicitud.objects.all()
    return render(request, 'combustible/lista_solicitudes.html', {'solicitudes': solicitudes})


@login_required
def crear_solicitud(request):
    clientes = CatalogoCliente.objects.prefetch_related('transportes').all()

    if request.method == 'POST':
        fecha_hora = request.POST.get('fecha_hora', '')
        cliente_ids = request.POST.getlist('cliente_id')
        anexo_2_list = request.POST.getlist('anexo_2')
        cantidades = request.POST.getlist('cant_abastecer')

        # Validar fecha
        if not fecha_hora:
            messages.error(request, 'La fecha y hora son obligatorias.')
            return render(request, 'combustible/crear_solicitud.html', {
                'clientes': clientes,
                'fecha_hora_temp': fecha_hora,
            })

        fecha_parseada = parse_datetime(fecha_hora)
        if fecha_parseada:
            if timezone.is_naive(fecha_parseada):
                fecha_parseada = timezone.make_aware(fecha_parseada)
            if fecha_parseada > timezone.now():
                messages.error(request, 'No se puede registrar una solicitud con fecha futura.')
                return render(request, 'combustible/crear_solicitud.html', {
                    'clientes': clientes,
                    'fecha_hora_temp': fecha_hora,
                })

        # Validar que haya al menos una fila
        if not cliente_ids:
            messages.error(request, 'Debe agregar al menos un cliente a la solicitud.')
            return render(request, 'combustible/crear_solicitud.html', {
                'clientes': clientes,
                'fecha_hora_temp': fecha_hora,
            })

        # Validar que no haya clientes duplicados
        if len(cliente_ids) != len(set(cliente_ids)):
            messages.error(request, 'No se puede repetir un cliente en la solicitud.')
            return render(request, 'combustible/crear_solicitud.html', {
                'clientes': clientes,
                'fecha_hora_temp': fecha_hora,
            })

        # Validar cantidades
        total_consumo = Decimal('0')
        total_venta = Decimal('0')

        for i, cliente_id in enumerate(cliente_ids):
            cliente = CatalogoCliente.objects.get(pk=cliente_id)
            cant_str = cantidades[i]
            anexo_2 = str(cliente_id) in anexo_2_list

            try:
                cantidad = Decimal(cant_str)
                if cantidad <= 0:
                    messages.error(request, f'La cantidad para {cliente.cliente} debe ser mayor que 0.')
                    return render(request, 'combustible/crear_solicitud.html', {
                        'clientes': clientes,
                        'fecha_hora_temp': fecha_hora,
                    })
            except InvalidOperation:
                messages.error(request, f'Cantidad inválida para {cliente.cliente}.')
                return render(request, 'combustible/crear_solicitud.html', {
                    'clientes': clientes,
                    'fecha_hora_temp': fecha_hora,
                })

            # Validar Anexo 2 para clientes de Venta
            if cliente.clasificacion == 'venta' and not anexo_2:
                messages.error(request, f'El cliente {cliente.cliente} es de Venta y debe tener el Anexo 2 aprobado.')
                return render(request, 'combustible/crear_solicitud.html', {
                    'clientes': clientes,
                    'fecha_hora_temp': fecha_hora,
                })

            # Sumar totales
            if cliente.clasificacion == 'venta':
                total_venta += cantidad
            else:
                total_consumo += cantidad

        total_general = total_consumo + total_venta

        # Crear solicitud
        solicitud = ModeloSolicitud.objects.create(
            fecha_hora=fecha_hora,
            estado='borrador',
            total_consumo=total_consumo,
            total_venta=total_venta,
            total_general=total_general
        )

        # Crear detalles y vehículos
        for i, cliente_id in enumerate(cliente_ids):
            cliente = CatalogoCliente.objects.get(pk=cliente_id)
            cant_str = cantidades[i]
            anexo_2 = str(cliente_id) in anexo_2_list

            detalle = DetalleSolicitud.objects.create(
                solicitud=solicitud,
                cliente=cliente,
                anexo_2=anexo_2,
                cant_abastecer=Decimal(cant_str)
            )

            # Guardar vehículos del cliente
            # Los datos vienen en formato: transporte_id|actividad|cantidad
            vehiculos_data = request.POST.getlist(f'vehiculos_{cliente_id}')
            for vehiculo_data in vehiculos_data:
                partes = vehiculo_data.split('|')
                if len(partes) == 3:
                    transporte_id = partes[0]
                    actividad = partes[1]
                    cantidad_vehiculo = partes[2]

                    DetalleSolicitudVehiculo.objects.create(
                        detalle_solicitud=detalle,
                        transporte_id=transporte_id,
                        actividad=actividad,
                        cant_abastecer=Decimal(cantidad_vehiculo)
                    )

        messages.success(request, 'Solicitud creada correctamente.')
        return redirect('lista_solicitudes')

    return render(request, 'combustible/crear_solicitud.html', {
        'clientes': clientes,
    })


@login_required
def ver_solicitud(request, pk):
    solicitud = get_object_or_404(ModeloSolicitud, pk=pk)
    detalles = DetalleSolicitud.objects.filter(solicitud=solicitud).select_related('cliente')

    # Obtener vehículos de cada detalle
    detalles_con_vehiculos = []
    for detalle in detalles:
        vehiculos = DetalleSolicitudVehiculo.objects.filter(detalle_solicitud=detalle).select_related('transporte')
        detalles_con_vehiculos.append({
            'detalle': detalle,
            'vehiculos': vehiculos
        })

    return render(request, 'combustible/ver_solicitud.html', {
        'solicitud': solicitud,
        'detalles_con_vehiculos': detalles_con_vehiculos,
    })


@login_required
def editar_solicitud(request, pk):
    solicitud = get_object_or_404(ModeloSolicitud, pk=pk)
    if solicitud.estado not in ['borrador', 'rechazada']:
        messages.error(request, 'Esta solicitud no se puede editar.')
        return redirect('lista_solicitudes')

    clientes = CatalogoCliente.objects.prefetch_related('transportes').all()
    detalles = DetalleSolicitud.objects.filter(solicitud=solicitud).select_related('cliente')

    # Preparar datos precargados
    detalles_precargados = []
    for detalle in detalles:
        vehiculos = DetalleSolicitudVehiculo.objects.filter(detalle_solicitud=detalle).select_related('transporte')
        vehiculos_data = []
        for v in vehiculos:
            vehiculos_data.append({
                'vehiculo_id': v.transporte.id,
                'tipo_vehiculo': v.transporte.tipo_vehiculo,
                'chapa': v.transporte.chapa,
                'actividad': v.actividad,
                'cantidad': str(v.cant_abastecer)
            })
        detalles_precargados.append({
            'cliente_id': detalle.cliente.id,
            'anexo_2': detalle.anexo_2,
            'cantidad': str(detalle.cant_abastecer),
            'vehiculos': vehiculos_data
        })

    if request.method == 'POST':
        fecha_hora = request.POST.get('fecha_hora', '')
        cliente_ids = request.POST.getlist('cliente_id')
        anexo_2_list = request.POST.getlist('anexo_2')
        cantidades = request.POST.getlist('cant_abastecer')

        # Validar fecha
        if not fecha_hora:
            messages.error(request, 'La fecha y hora son obligatorias.')
            return render(request, 'combustible/editar_solicitud.html', {
                'solicitud': solicitud,
                'clientes': clientes,
                'detalles_precargados': detalles_precargados,
                'fecha_hora_temp': fecha_hora,
            })

        fecha_parseada = parse_datetime(fecha_hora)
        if fecha_parseada:
            if timezone.is_naive(fecha_parseada):
                fecha_parseada = timezone.make_aware(fecha_parseada)
            if fecha_parseada > timezone.now():
                messages.error(request, 'No se puede registrar una solicitud con fecha futura.')
                return render(request, 'combustible/editar_solicitud.html', {
                    'solicitud': solicitud,
                    'clientes': clientes,
                    'detalles_precargados': detalles_precargados,
                    'fecha_hora_temp': fecha_hora,
                })

        # Validar que haya al menos una fila
        if not cliente_ids:
            messages.error(request, 'Debe agregar al menos un cliente a la solicitud.')
            return render(request, 'combustible/editar_solicitud.html', {
                'solicitud': solicitud,
                'clientes': clientes,
                'detalles_precargados': detalles_precargados,
                'fecha_hora_temp': fecha_hora,
            })

        # Validar que no haya clientes duplicados
        if len(cliente_ids) != len(set(cliente_ids)):
            messages.error(request, 'No se puede repetir un cliente en la solicitud.')
            return render(request, 'combustible/editar_solicitud.html', {
                'solicitud': solicitud,
                'clientes': clientes,
                'detalles_precargados': detalles_precargados,
                'fecha_hora_temp': fecha_hora,
            })

        # Validar cantidades
        total_consumo = Decimal('0')
        total_venta = Decimal('0')

        for i, cliente_id in enumerate(cliente_ids):
            cliente = CatalogoCliente.objects.get(pk=cliente_id)
            cant_str = cantidades[i]
            anexo_2 = str(cliente_id) in anexo_2_list

            try:
                cantidad = Decimal(cant_str)
                if cantidad <= 0:
                    messages.error(request, f'La cantidad para {cliente.cliente} debe ser mayor que 0.')
                    return render(request, 'combustible/editar_solicitud.html', {
                        'solicitud': solicitud,
                        'clientes': clientes,
                        'detalles_precargados': detalles_precargados,
                        'fecha_hora_temp': fecha_hora,
                    })
            except InvalidOperation:
                messages.error(request, f'Cantidad inválida para {cliente.cliente}.')
                return render(request, 'combustible/editar_solicitud.html', {
                    'solicitud': solicitud,
                    'clientes': clientes,
                    'detalles_precargados': detalles_precargados,
                    'fecha_hora_temp': fecha_hora,
                })

            # Validar Anexo 2 para clientes de Venta
            if cliente.clasificacion == 'venta' and not anexo_2:
                messages.error(request, f'El cliente {cliente.cliente} es de Venta y debe tener el Anexo 2 aprobado.')
                return render(request, 'combustible/editar_solicitud.html', {
                    'solicitud': solicitud,
                    'clientes': clientes,
                    'detalles_precargados': detalles_precargados,
                    'fecha_hora_temp': fecha_hora,
                })

            # Sumar totales
            if cliente.clasificacion == 'venta':
                total_venta += cantidad
            else:
                total_consumo += cantidad

        total_general = total_consumo + total_venta

        # Actualizar solicitud
        solicitud.fecha_hora = fecha_hora
        solicitud.estado = 'borrador'
        solicitud.motivo_rechazo = None
        solicitud.total_consumo = total_consumo
        solicitud.total_venta = total_venta
        solicitud.total_general = total_general
        solicitud.save()

        # Eliminar detalles antiguos
        DetalleSolicitud.objects.filter(solicitud=solicitud).delete()

        # Crear nuevos detalles y vehículos
        for i, cliente_id in enumerate(cliente_ids):
            cliente = CatalogoCliente.objects.get(pk=cliente_id)
            cant_str = cantidades[i]
            anexo_2 = str(cliente_id) in anexo_2_list

            detalle = DetalleSolicitud.objects.create(
                solicitud=solicitud,
                cliente=cliente,
                anexo_2=anexo_2,
                cant_abastecer=Decimal(cant_str)
            )

            # Guardar vehículos del cliente
            vehiculos_data = request.POST.getlist(f'vehiculos_{cliente_id}')
            for vehiculo_data in vehiculos_data:
                partes = vehiculo_data.split('|')
                if len(partes) == 3:
                    transporte_id = partes[0]
                    actividad = partes[1]
                    cantidad_vehiculo = partes[2]

                    DetalleSolicitudVehiculo.objects.create(
                        detalle_solicitud=detalle,
                        transporte_id=transporte_id,
                        actividad=actividad,
                        cant_abastecer=Decimal(cantidad_vehiculo)
                    )

        messages.success(request, 'Solicitud modificada correctamente.')
        return redirect('lista_solicitudes')

    return render(request, 'combustible/editar_solicitud.html', {
        'solicitud': solicitud,
        'clientes': clientes,
        'detalles_precargados': detalles_precargados,
    })


@login_required
def enviar_solicitud(request, pk):
    solicitud = get_object_or_404(ModeloSolicitud, pk=pk)
    if solicitud.estado in ['borrador', 'rechazada']:
        solicitud.estado = 'pendiente'
        solicitud.save()
        messages.success(request, 'Solicitud enviada correctamente.')
    else:
        messages.error(request, 'Esta solicitud no se puede enviar.')
    return redirect('lista_solicitudes')


@login_required
def eliminar_solicitud(request, pk):
    solicitud = get_object_or_404(ModeloSolicitud, pk=pk)
    if solicitud.estado not in ['borrador', 'rechazada']:
        messages.error(request, 'Esta solicitud no se puede eliminar.')
        return redirect('lista_solicitudes')
    solicitud.delete()
    messages.success(request, 'Solicitud eliminada correctamente.')
    return redirect('lista_solicitudes')
