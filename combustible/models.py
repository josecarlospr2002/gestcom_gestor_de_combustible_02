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


class SuministroCombustible(models.Model):
    ESTADOS_SUMINISTRO = [
        ('pendiente', 'Pendiente a Validar'),
        ('validado', 'Validado'),
    ]

    fecha_hora = models.DateTimeField(verbose_name='Fecha y Hora')
    cantidad = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name='Cantidad a Insertar'
    )
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción / Nota')
    cantidad_antes = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name='Cantidad Antes de Insertar'
    )
    cantidad_despues = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name='Cantidad Después de Insertar'
    )
    estado = models.CharField(max_length=20, choices=ESTADOS_SUMINISTRO, default='pendiente', verbose_name='Estado')

    class Meta:
        verbose_name = 'Suministro de Combustible'
        verbose_name_plural = 'Suministros de Combustible'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"Suministro #{self.id} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
