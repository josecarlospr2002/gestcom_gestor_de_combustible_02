from django.contrib import admin
from .models import CatalogoCliente, Transporte, ModeloSolicitud, DetalleSolicitud


@admin.register(CatalogoCliente)
class CatalogoClienteAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'clasificacion', 'no_contrato')
    list_filter = ('clasificacion',)
    search_fields = ('cliente', 'no_contrato')


@admin.register(Transporte)
class TransporteAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo_vehiculo', 'chapa', 'ic')
    list_filter = ('cliente',)
    search_fields = ('tipo_vehiculo', 'chapa', 'cliente__cliente')


@admin.register(ModeloSolicitud)
class ModeloSolicitudAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_hora', 'estado', 'total_consumo', 'total_venta', 'total_general')
    list_filter = ('estado', 'fecha_hora')


@admin.register(DetalleSolicitud)
class DetalleSolicitudAdmin(admin.ModelAdmin):
    list_display = ('solicitud', 'cliente', 'anexo_2', 'cant_abastecer')
    list_filter = ('anexo_2',)