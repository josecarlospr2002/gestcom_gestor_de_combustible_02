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