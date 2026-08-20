from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from .models import CatalogoCliente, Transporte, ModeloSolicitud, DetalleSolicitud, DetalleSolicitudVehiculo, \
    AlmacenProduccion, AlmacenAseguramiento, TransferenciaAlmacen, OperacionAlmacenProduccion, SuministroCombustible
from .forms import CatalogoClienteForm, TransporteForm, TransferenciaAlmacenForm, OperacionAlmacenProduccionForm, \
    SuministroCombustibleForm


@login_required
def dashboard(request):
    almacen = AlmacenProduccion.objects.first()
    cantidad_almacen = almacen.cantidad_actual if almacen else 0
    return render(request, 'combustible/dashboard.html', {
        'cantidad_almacen': cantidad_almacen,
    })


# Vistas para Catálogo de Cliente
@login_required
def lista_clientes(request):
    if request.user.departamento not in ['admin', 'transporte', 'directivo', 'director']:
        messages.error(request, 'No tiene permisos para ver el catálogo de clientes.')
        return redirect('dashboard')
    clientes = CatalogoCliente.objects.all()
    puede_editar = request.user.departamento in ['admin', 'directivo']
    return render(request, 'combustible/lista_clientes.html', {
        'clientes': clientes,
        'puede_editar': puede_editar,
    })


@login_required
def crear_cliente(request):
    if request.user.departamento not in ['admin', 'transporte']:
        messages.error(request, 'No tiene permisos para crear clientes.')
        return redirect('lista_clientes')
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
    if request.user.departamento not in ['admin', 'directivo']:
        messages.error(request, 'No tiene permisos para modificar clientes.')
        return redirect('lista_clientes')
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
    if request.user.departamento not in ['admin']:
        messages.error(request, 'No tiene permisos para ver el transporte.')
        return redirect('dashboard')
    transportes = Transporte.objects.select_related('cliente').all()
    puede_editar = request.user.departamento in ['admin']
    return render(request, 'combustible/lista_transporte.html', {
        'transportes': transportes,
        'puede_editar': puede_editar,
    })


@login_required
def crear_vehiculo(request):
    if request.user.departamento not in ['admin', 'transporte']:
        messages.error(request, 'No tiene permisos para crear vehículos.')
        return redirect('dashboard')

    cliente_inicial = None
    cliente_id = request.GET.get('cliente_id') or request.POST.get('cliente')

    if cliente_id:
        try:
            cliente_inicial = CatalogoCliente.objects.get(pk=cliente_id)
        except CatalogoCliente.DoesNotExist:
            cliente_inicial = None

    if request.method == 'POST':
        form = TransporteForm(request.POST)
        if form.is_valid():
            vehiculo = form.save()
            messages.success(request, 'Vehículo agregado correctamente.')
            # Si venía de un cliente específico, redirigir a ver_cliente
            if cliente_inicial:
                return redirect('ver_cliente', pk=cliente_inicial.pk)
            return redirect('lista_transporte')
        else:
            messages.error(request, 'Por favor, corrija los errores señalados.')
    else:
        initial = {}
        if cliente_inicial:
            initial['cliente'] = cliente_inicial
        form = TransporteForm(initial=initial)
        # Deshabilitar el campo cliente si viene preseleccionado
        if cliente_inicial:
            form.fields['cliente'].queryset = CatalogoCliente.objects.filter(pk=cliente_inicial.pk)
            form.fields['cliente'].initial = cliente_inicial
            form.fields['cliente'].widget.attrs['readonly'] = True
            form.fields['cliente'].widget.attrs['disabled'] = 'disabled'

    return render(request, 'combustible/crear_vehiculo.html', {
        'form': form,
        'cliente_inicial': cliente_inicial,
    })


@login_required
def editar_vehiculo(request, pk):
    if request.user.departamento not in ['admin', 'transporte']:
        messages.error(request, 'No tiene permisos para modificar vehículos.')
        return redirect('dashboard')
    vehiculo = get_object_or_404(Transporte, pk=pk)

    # Detectar si viene desde ver_cliente
    desde_cliente = request.GET.get('desde_cliente', False)

    if request.method == 'POST':
        form = TransporteForm(request.POST, instance=vehiculo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehículo modificado correctamente.')
            if desde_cliente:
                return redirect('ver_cliente', pk=vehiculo.cliente.pk)
            return redirect('lista_transporte')
        else:
            messages.error(request, 'Por favor, corrija los errores señalados.')
    else:
        form = TransporteForm(instance=vehiculo)
        if desde_cliente:
            # Bloquear campo cliente
            form.fields['cliente'].widget.attrs['readonly'] = True
            form.fields['cliente'].widget.attrs['disabled'] = 'disabled'

    return render(request, 'combustible/editar_vehiculo.html', {
        'form': form,
        'vehiculo': vehiculo,
        'desde_cliente': desde_cliente,
    })


@login_required
def eliminar_vehiculo(request, pk):
    if request.user.departamento not in ['admin', 'transporte']:
        messages.error(request, 'No tiene permisos para eliminar vehículos.')
        return redirect('dashboard')
    vehiculo = get_object_or_404(Transporte, pk=pk)
    cliente_pk = vehiculo.cliente.pk
    vehiculo.delete()
    messages.success(request, 'Vehículo eliminado correctamente.')
    return redirect('ver_cliente', pk=cliente_pk)


@login_required
def ver_cliente(request, pk):
    if request.user.departamento not in ['admin', 'transporte', 'directivo', 'director']:
        messages.error(request, 'No tiene permisos para ver este cliente.')
        return redirect('dashboard')
    cliente = get_object_or_404(CatalogoCliente, pk=pk)
    vehiculos = Transporte.objects.filter(cliente=cliente)
    puede_editar = request.user.departamento in ['admin', 'transporte']
    return render(request, 'combustible/ver_cliente.html', {
        'cliente': cliente,
        'vehiculos': vehiculos,
        'puede_editar': puede_editar,
    })


# Vistas para Modelo de Solicitud
@login_required
def lista_solicitudes(request):
    if request.user.departamento not in ['admin', 'transporte', 'directivo', 'director']:
        messages.error(request, 'No tiene permisos para ver las solicitudes.')
        return redirect('dashboard')
    solicitudes = ModeloSolicitud.objects.all()
    puede_editar = request.user.departamento in ['admin', 'transporte']
    puede_aprobar = request.user.departamento in ['admin', 'director']

    # Verificar si hay al menos una solicitud con acciones disponibles para este usuario
    hay_acciones = False

    if puede_editar:
        hay_acciones = solicitudes.filter(estado__in=['borrador', 'rechazada']).exists()

    if not hay_acciones and puede_aprobar:
        hay_acciones = solicitudes.filter(estado='pendiente').exists()

    return render(request, 'combustible/lista_solicitudes.html', {
        'solicitudes': solicitudes,
        'puede_editar': puede_editar,
        'puede_aprobar': puede_aprobar,
        'hay_acciones': hay_acciones,
    })


@login_required
def crear_solicitud(request):
    if request.user.departamento not in ['admin', 'transporte']:
        messages.error(request, 'No tiene permisos para crear solicitudes.')
        return redirect('lista_solicitudes')
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
    if request.user.departamento not in ['admin', 'transporte', 'directivo', 'director']:
        messages.error(request, 'No tiene permisos para ver esta solicitud.')
        return redirect('dashboard')
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
    if request.user.departamento not in ['admin', 'transporte']:
        messages.error(request, 'No tiene permisos para modificar solicitudes.')
        return redirect('lista_solicitudes')
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
    if request.user.departamento not in ['admin', 'transporte']:
        messages.error(request, 'No tiene permisos para enviar solicitudes.')
        return redirect('lista_solicitudes')
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
    if request.user.departamento not in ['admin', 'transporte']:
        messages.error(request, 'No tiene permisos para eliminar solicitudes.')
        return redirect('lista_solicitudes')
    solicitud = get_object_or_404(ModeloSolicitud, pk=pk)
    if solicitud.estado not in ['borrador', 'rechazada']:
        messages.error(request, 'Esta solicitud no se puede eliminar.')
        return redirect('lista_solicitudes')
    solicitud.delete()
    messages.success(request, 'Solicitud eliminada correctamente.')
    return redirect('lista_solicitudes')


@login_required
def aprobar_solicitud(request, pk):
    if request.user.departamento not in ['admin', 'director']:
        messages.error(request, 'No tiene permisos para aprobar solicitudes.')
        return redirect('lista_solicitudes')
    solicitud = get_object_or_404(ModeloSolicitud, pk=pk)
    if solicitud.estado != 'pendiente':
        messages.error(request, 'Esta solicitud no se puede aprobar.')
        return redirect('lista_solicitudes')
    solicitud.estado = 'aprobada'
    solicitud.save()

    # Crear registro en TransferenciaAlmacen automáticamente
    almacen_aseguramiento = AlmacenAseguramiento.objects.first()
    if not almacen_aseguramiento:
        almacen_aseguramiento = AlmacenAseguramiento.objects.create(cantidad_actual=0)

    TransferenciaAlmacen.objects.create(
        solicitud=solicitud,
        saldo_aseguramiento=almacen_aseguramiento.cantidad_actual,
        estado='pendiente'
    )

    messages.success(request, f'Solicitud #{solicitud.id} aprobada correctamente.')
    return redirect('lista_solicitudes')


@login_required
def rechazar_solicitud(request, pk):
    if request.user.departamento not in ['admin', 'director']:
        messages.error(request, 'No tiene permisos para rechazar solicitudes.')
        return redirect('lista_solicitudes')
    solicitud = get_object_or_404(ModeloSolicitud, pk=pk)
    if solicitud.estado != 'pendiente':
        messages.error(request, 'Esta solicitud no se puede rechazar.')
        return redirect('lista_solicitudes')
    solicitud.estado = 'rechazada'
    solicitud.motivo_rechazo = request.GET.get('motivo', '')
    solicitud.save()
    messages.success(request, f'Solicitud #{solicitud.id} rechazada correctamente.')
    return redirect('lista_solicitudes')


@login_required
def lista_suministros(request):
    if request.user.departamento not in ['admin', 'petroleo']:
        messages.error(request, 'No tiene permisos para ver los suministros.')
        return redirect('dashboard')
    suministros = SuministroCombustible.objects.all().order_by('-fecha_hora')
    almacen = AlmacenProduccion.objects.first()
    if not almacen:
        almacen = AlmacenProduccion.objects.create(cantidad_actual=0)

    # Verificar si hay acciones disponibles (algún suministro pendiente)
    puede_editar = request.user.departamento in ['admin', 'petroleo']
    hay_acciones = puede_editar and suministros.filter(estado='pendiente').exists()

    return render(request, 'combustible/lista_suministros.html', {
        'suministros': suministros,
        'almacen': almacen,
        'hay_acciones': hay_acciones,
        'puede_editar': puede_editar,
    })


@login_required
def crear_suministro(request):
    if request.user.departamento not in ['admin', 'petroleo']:
        messages.error(request, 'No tiene permisos para crear suministros.')
        return redirect('lista_suministros')

    almacen = AlmacenProduccion.objects.first()
    if not almacen:
        almacen = AlmacenProduccion.objects.create(cantidad_actual=0)

    if request.method == 'POST':
        form = SuministroCombustibleForm(request.POST)
        if form.is_valid():
            suministro = form.save(commit=False)
            suministro.cantidad_antes = almacen.cantidad_actual
            suministro.cantidad_despues = almacen.cantidad_actual
            suministro.estado = 'pendiente'
            suministro.save()
            messages.success(request, 'Suministro creado correctamente. Pendiente de validar.')
            return redirect('lista_suministros')
        else:
            messages.error(request, 'Por favor, corrija los errores señalados.')
    else:
        form = SuministroCombustibleForm()

    return render(request, 'combustible/crear_suministro.html', {'form': form})


@login_required
def editar_suministro(request, pk):
    if request.user.departamento not in ['admin', 'petroleo']:
        messages.error(request, 'No tiene permisos para modificar suministros.')
        return redirect('lista_suministros')

    suministro = get_object_or_404(SuministroCombustible, pk=pk)
    if suministro.estado != 'pendiente':
        messages.error(request, 'Este suministro no se puede modificar.')
        return redirect('lista_suministros')

    if request.method == 'POST':
        form = SuministroCombustibleForm(request.POST, instance=suministro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Suministro modificado correctamente.')
            return redirect('lista_suministros')
        else:
            messages.error(request, 'Por favor, corrija los errores señalados.')
    else:
        form = SuministroCombustibleForm(instance=suministro)

    return render(request, 'combustible/editar_suministro.html', {'form': form, 'suministro': suministro})


@login_required
def validar_suministro(request, pk):
    if request.user.departamento not in ['admin', 'petroleo']:
        messages.error(request, 'No tiene permisos para validar suministros.')
        return redirect('lista_suministros')

    suministro = get_object_or_404(SuministroCombustible, pk=pk)
    if suministro.estado != 'pendiente':
        messages.error(request, 'Este suministro no se puede validar.')
        return redirect('lista_suministros')

    almacen = AlmacenProduccion.objects.first()
    if not almacen:
        almacen = AlmacenProduccion.objects.create(cantidad_actual=0)

    # Actualizar almacén
    almacen.cantidad_actual += suministro.cantidad
    almacen.save()

    # Actualizar suministro
    suministro.cantidad_despues = almacen.cantidad_actual
    suministro.estado = 'validado'
    suministro.save()

    messages.success(request, 'Suministro validado correctamente. Combustible agregado al almacén.')
    return redirect('lista_suministros')


@login_required
def ver_suministro(request, pk):
    if request.user.departamento not in ['admin', 'petroleo']:
        messages.error(request, 'No tiene permisos para ver este suministro.')
        return redirect('lista_suministros')

    suministro = get_object_or_404(SuministroCombustible, pk=pk)
    return render(request, 'combustible/ver_suministro.html', {
        'suministro': suministro,
    })


@login_required
def eliminar_suministro(request, pk):
    if request.user.departamento not in ['admin', 'petroleo']:
        messages.error(request, 'No tiene permisos para eliminar suministros.')
        return redirect('lista_suministros')

    suministro = get_object_or_404(SuministroCombustible, pk=pk)
    if suministro.estado != 'pendiente':
        messages.error(request, 'Este suministro no se puede eliminar.')
        return redirect('lista_suministros')

    suministro.delete()
    messages.success(request, 'Suministro eliminado correctamente.')
    return redirect('lista_suministros')


# Vistas para Transferencia entre Almacenes
@login_required
def lista_transferencias(request):
    if request.user.departamento not in ['admin', 'petroleo', 'director', 'directivo']:
        messages.error(request, 'No tiene permisos para ver las transferencias.')
        return redirect('dashboard')

    transferencias = TransferenciaAlmacen.objects.select_related('solicitud').all().order_by('-id')
    almacen_aseguramiento = AlmacenAseguramiento.objects.first()
    if not almacen_aseguramiento:
        almacen_aseguramiento = AlmacenAseguramiento.objects.create(cantidad_actual=0)

    puede_editar = request.user.departamento in ['admin', 'petroleo']
    hay_acciones = puede_editar and transferencias.filter(estado='pendiente',
                                                          cantidad_transferida__isnull=False).exists()
    return render(request, 'combustible/lista_transferencias.html', {
        'transferencias': transferencias,
        'almacen_aseguramiento': almacen_aseguramiento,
        'puede_editar': puede_editar,
        'hay_acciones': hay_acciones,
    })


@login_required
def guardar_transferencia(request, pk):
    if request.user.departamento not in ['admin', 'petroleo']:
        messages.error(request, 'No tiene permisos para guardar transferencias.')
        return redirect('lista_transferencias')

    transferencia = get_object_or_404(TransferenciaAlmacen, pk=pk)
    if transferencia.estado != 'pendiente':
        messages.error(request, 'Esta transferencia no se puede modificar.')
        return redirect('lista_transferencias')

    if request.method == 'POST':
        form = TransferenciaAlmacenForm(request.POST, instance=transferencia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transferencia guardada correctamente.')
            return redirect('lista_transferencias')
        else:
            messages.error(request, 'Por favor, corrija los errores señalados.')
            return redirect('lista_transferencias')

    return redirect('lista_transferencias')


@login_required
def confirmar_transferencia(request, pk):
    if request.user.departamento not in ['admin', 'petroleo']:
        messages.error(request, 'No tiene permisos para confirmar transferencias.')
        return redirect('lista_transferencias')

    transferencia = get_object_or_404(TransferenciaAlmacen, pk=pk)
    if transferencia.estado != 'pendiente':
        messages.error(request, 'Esta transferencia no se puede confirmar.')
        return redirect('lista_transferencias')

    if not transferencia.cantidad_transferida or transferencia.cantidad_transferida <= 0:
        messages.error(request, 'Debe guardar una cantidad de transferencia válida antes de confirmar.')
        return redirect('lista_transferencias')

    transferencia.estado = 'transferido'
    transferencia.save()

    messages.success(request, f'Transferencia #{transferencia.id} confirmada correctamente.')
    return redirect('lista_transferencias')


# Vistas para Operaciones de Almacén de Producción
@login_required
def lista_operaciones_almacen(request):
    if request.user.departamento not in ['admin', 'petroleo', 'director', 'directivo']:
        messages.error(request, 'No tiene permisos para ver las operaciones del almacén.')
        return redirect('dashboard')

    operaciones = OperacionAlmacenProduccion.objects.all().order_by('-id')
    almacen = AlmacenProduccion.objects.first()
    if not almacen:
        almacen = AlmacenProduccion.objects.create(cantidad_actual=0)

    puede_editar = request.user.departamento in ['admin', 'petroleo']

    return render(request, 'combustible/lista_operaciones_almacen.html', {
        'operaciones': operaciones,
        'almacen': almacen,
        'puede_editar': puede_editar,
    })


@login_required
def crear_operacion_almacen(request):
    if request.user.departamento not in ['admin', 'petroleo']:
        messages.error(request, 'No tiene permisos para crear operaciones.')
        return redirect('lista_operaciones_almacen')

    # Obtener la última operación para la existencia
    ultima_operacion = OperacionAlmacenProduccion.objects.order_by('-id').first()

    # Obtener el almacén de producción
    almacen = AlmacenProduccion.objects.first()
    if not almacen:
        almacen = AlmacenProduccion.objects.create(cantidad_actual=0)

    # Determinar la existencia actual
    if ultima_operacion:
        existencia = ultima_operacion.nueva_existencia
    else:
        existencia = almacen.cantidad_actual

    # Calcular transferencias no contadas
    transferencia = Decimal('0')
    if ultima_operacion:
        # Buscar transferencias confirmadas después del último registro
        transferencias_pendientes = TransferenciaAlmacen.objects.filter(
            estado='transferido',
            fecha_hora__gt=ultima_operacion.fecha_hora
        )
    else:
        # Primera operación: buscar todas las transferencias confirmadas
        transferencias_pendientes = TransferenciaAlmacen.objects.filter(estado='transferido')

    for t in transferencias_pendientes:
        if t.cantidad_transferida:
            transferencia += t.cantidad_transferida

    if request.method == 'POST':
        form = OperacionAlmacenProduccionForm(request.POST)
        if form.is_valid():
            operacion = form.save(commit=False)
            operacion.existencia = existencia
            operacion.transferencia = transferencia
            operacion.nueva_existencia = (existencia + operacion.entrada_factura) - operacion.generacion - transferencia
            operacion.save()

            # Actualizar el almacén de producción
            almacen.cantidad_actual = operacion.nueva_existencia
            almacen.save()

            messages.success(request, 'Operación registrada correctamente.')
            return redirect('lista_operaciones_almacen')
        else:
            messages.error(request, 'Por favor, corrija los errores señalados.')
    else:
        form = OperacionAlmacenProduccionForm()

    return render(request, 'combustible/crear_operacion_almacen.html', {
        'form': form,
        'existencia': existencia,
        'transferencia': transferencia,
    })