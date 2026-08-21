from django.db import models
from django.core.validators import MinValueValidator


class CatalogoCliente(models.Model):
    CLASIFICACIONES = [
        ('consumo', 'Consumo'),
        ('venta', 'Venta'),
        ('factura', 'En Factura de Servicio'),
    ]

    cliente = models.CharField(max_length=100, verbose_name='Cliente')
    clasificacion = models.CharField(
        max_length=20,
        choices=CLASIFICACIONES,
        verbose_name='Clasificación'
    )
    no_contrato = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='No. Contrato'
    )

    class Meta:
        verbose_name = 'Catálogo de Cliente'
        verbose_name_plural = 'Catálogo de Clientes'
        ordering = ['cliente']

    def __str__(self):
        return f"{self.cliente}"


class Transporte(models.Model):
    cliente = models.ForeignKey(
        CatalogoCliente,
        on_delete=models.CASCADE,
        related_name='transportes',
        verbose_name='Cliente'
    )
    tipo_vehiculo = models.CharField(max_length=50, verbose_name='Tipo de Vehículo')
    chapa = models.CharField(max_length=20, verbose_name='Chapa')
    ic = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='I/C'
    )

    class Meta:
        verbose_name = 'Transporte'
        verbose_name_plural = 'Transportes'
        ordering = ['cliente', 'tipo_vehiculo']

    def __str__(self):
        return f"{self.cliente.cliente} - {self.tipo_vehiculo} - {self.chapa}"


class ModeloSolicitud(models.Model):
    ESTADOS = [
        ('borrador', 'Borrador'),
        ('pendiente', 'Pendiente a Revisión'),
        ('aprobada', 'Aprobada por el Director'),
        ('rechazada', 'Rechazada por el Director'),
    ]

    fecha_hora = models.DateTimeField(verbose_name='Fecha y Hora')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='borrador', verbose_name='Estado')
    motivo_rechazo = models.TextField(blank=True, null=True, verbose_name='Motivo del Rechazo')
    total_consumo = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Total de Consumo')
    total_venta = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Total de Venta')
    total_general = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Total General')

    class Meta:
        verbose_name = 'Modelo de Solicitud'
        verbose_name_plural = 'Modelos de Solicitudes'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"Modelo de Solicitud #{self.id} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"


class DetalleSolicitud(models.Model):
    solicitud = models.ForeignKey(ModeloSolicitud, on_delete=models.CASCADE, related_name='detalles')
    cliente = models.ForeignKey(CatalogoCliente, on_delete=models.CASCADE, verbose_name='Cliente')
    anexo_2 = models.BooleanField(default=False, verbose_name='Anexo 2')
    cant_abastecer = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Cant. a Abastecer')

    class Meta:
        verbose_name = 'Detalle de Solicitud'
        verbose_name_plural = 'Detalles de Solicitudes'

    def __str__(self):
        return f"{self.cliente.cliente} - {self.solicitud}"


class DetalleSolicitudVehiculo(models.Model):
    detalle_solicitud = models.ForeignKey(DetalleSolicitud, on_delete=models.CASCADE, related_name='vehiculos')
    transporte = models.ForeignKey(Transporte, on_delete=models.CASCADE, verbose_name='Transporte')
    actividad = models.CharField(max_length=100, verbose_name='Actividad')
    cant_abastecer = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Cant. a Abastecer')

    class Meta:
        verbose_name = 'Detalle de Solicitud - Vehículo'
        verbose_name_plural = 'Detalles de Solicitudes - Vehículos'

    def __str__(self):
        return f"{self.transporte.chapa} - {self.cant_abastecer}"


class AlmacenProduccion(models.Model):
    cantidad_actual = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name='Cantidad Actual de Combustible'
    )

    class Meta:
        verbose_name = 'Almacén de Producción'
        verbose_name_plural = 'Almacén de Producción'

    def __str__(self):
        return f"Almacén de Producción - {self.cantidad_actual} L"


class AlmacenAseguramiento(models.Model):
    cantidad_actual = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name='Cantidad Actual de Combustible'
    )

    class Meta:
        verbose_name = 'Almacén de Aseguramiento'
        verbose_name_plural = 'Almacén de Aseguramiento'

    def __str__(self):
        return f"Almacén de Aseguramiento - {self.cantidad_actual} L"


class TransferenciaAlmacen(models.Model):
    ESTADOS_TRANSFERENCIA = [
        ('pendiente', 'Pendiente'),
        ('transferido', 'Transferido'),
    ]

    solicitud = models.OneToOneField(
        ModeloSolicitud,
        on_delete=models.CASCADE,
        related_name='transferencia',
        verbose_name='Solicitud Aprobada'
    )
    fecha_hora = models.DateTimeField(null=True, blank=True, verbose_name='Fecha y Hora de Transferencia')
    saldo_aseguramiento = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name='Saldo en Almacén de Aseguramiento'
    )
    cantidad_transferida = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Transferencia'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_TRANSFERENCIA,
        default='pendiente',
        verbose_name='Estado'
    )

    class Meta:
        verbose_name = 'Transferencia entre Almacenes'
        verbose_name_plural = 'Transferencias entre Almacenes'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"Transferencia #{self.id} - Solicitud #{self.solicitud.id}"


class OperacionAlmacenProduccion(models.Model):
    ESTADOS_OPERACION = [
        ('pendiente', 'Pendiente'),
        ('validado', 'Validado'),
    ]

    fecha_hora = models.DateTimeField(verbose_name='Fecha y Hora')
    existencia = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name='Existencia'
    )
    entrada_factura = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name='Entrada por Factura'
    )
    generacion = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name='Generación'
    )
    transferencia = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name='Transferencia'
    )
    nueva_existencia = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name='Nueva Existencia'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_OPERACION,
        default='pendiente',
        verbose_name='Estado'
    )

    class Meta:
        verbose_name = 'Operación de Almacén de Producción'
        verbose_name_plural = 'Operaciones de Almacén de Producción'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"Operación #{self.id} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"


class RegistroAlmacenAseguramiento(models.Model):
    ESTADOS_REGISTRO = [
        ('pendiente', 'Pendiente'),
        ('despachado', 'Despachado'),
    ]

    solicitud = models.ForeignKey(
        ModeloSolicitud,
        on_delete=models.CASCADE,
        related_name='registros_aseguramiento',
        verbose_name='Solicitud'
    )
    fecha_hora = models.DateTimeField(verbose_name='Fecha y Hora')
    cantidad_total_aprobada = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name='Cantidad Total Aprobada'
    )
    despacho_real_total = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name='Despacho Real Total'
    )
    total_consumo = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name='Total de Consumo Sobrante'
    )
    total_venta = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name='Total de Venta Sobrante'
    )
    total_existente = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name='Total Existente'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_REGISTRO,
        default='pendiente',
        verbose_name='Estado'
    )

    class Meta:
        verbose_name = 'Registro de Almacén de Aseguramiento'
        verbose_name_plural = 'Registros de Almacén de Aseguramiento'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"Registro #{self.id} - Solicitud #{self.solicitud.id}"


class DespachoRealVehiculo(models.Model):
    registro = models.ForeignKey(
        RegistroAlmacenAseguramiento,
        on_delete=models.CASCADE,
        related_name='despachos',
        verbose_name='Registro'
    )
    detalle_vehiculo = models.ForeignKey(
        DetalleSolicitudVehiculo,
        on_delete=models.CASCADE,
        verbose_name='Vehículo de Solicitud'
    )
    despacho_real = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Despacho Real'
    )

    class Meta:
        verbose_name = 'Despacho Real por Vehículo'
        verbose_name_plural = 'Despachos Reales por Vehículos'

    def __str__(self):
        return f"{self.detalle_vehiculo.transporte.chapa} - {self.despacho_real}"


class ResultadoAlmacenAseguramiento(models.Model):
    registro = models.OneToOneField(
        RegistroAlmacenAseguramiento,
        on_delete=models.CASCADE,
        related_name='resultado',
        verbose_name='Registro'
    )
    fecha_hora = models.DateTimeField(verbose_name='Fecha y Hora')
    total_consumo = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name='Total de Consumo'
    )
    total_venta = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name='Total de Venta'
    )
    total_existente = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name='Total Existente'
    )

    class Meta:
        verbose_name = 'Resultado de Almacén de Aseguramiento'
        verbose_name_plural = 'Resultados de Almacén de Aseguramiento'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"Resultado #{self.id} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"