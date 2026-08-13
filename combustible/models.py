from django.db import models


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
        return f"{self.cliente} - {self.get_clasificacion_display()}"