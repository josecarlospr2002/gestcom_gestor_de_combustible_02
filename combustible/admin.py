from django.contrib import admin
from .models import CatalogoCliente, Transporte, ModeloSolicitud, DetalleSolicitud, DetalleSolicitudVehiculo, \
    AlmacenProduccion, AlmacenAseguramiento, TransferenciaAlmacen, OperacionAlmacenProduccion, \
    RegistroAlmacenAseguramiento, DespachoRealVehiculo


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


@admin.register(DetalleSolicitudVehiculo)
class DetalleSolicitudVehiculoAdmin(admin.ModelAdmin):
    list_display = ('detalle_solicitud', 'transporte', 'actividad', 'cant_abastecer')
    search_fields = ('transporte__chapa', 'actividad')


@admin.register(AlmacenProduccion)
class AlmacenProduccionAdmin(admin.ModelAdmin):
    list_display = ('cantidad_actual',)


@admin.register(AlmacenAseguramiento)
class AlmacenAseguramientoAdmin(admin.ModelAdmin):
    list_display = ('cantidad_actual',)


@admin.register(TransferenciaAlmacen)
class TransferenciaAlmacenAdmin(admin.ModelAdmin):
    list_display = ('id', 'solicitud', 'fecha_hora', 'saldo_aseguramiento', 'cantidad_transferida', 'estado')
    list_filter = ('estado', 'fecha_hora')
    search_fields = ('solicitud__id',)


@admin.register(OperacionAlmacenProduccion)
class OperacionAlmacenProduccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_hora', 'existencia', 'entrada_factura', 'generacion', 'transferencia', 'nueva_existencia', 'estado')
    list_filter = ('estado', 'fecha_hora')


@admin.register(RegistroAlmacenAseguramiento)
class RegistroAlmacenAseguramientoAdmin(admin.ModelAdmin):
    list_display = ('id', 'solicitud', 'fecha_hora', 'cantidad_total_aprobada', 'despacho_real_total', 'estado')
    list_filter = ('estado', 'fecha_hora')
    search_fields = ('solicitud__id',)


@admin.register(DespachoRealVehiculo)
class DespachoRealVehiculoAdmin(admin.ModelAdmin):
    list_display = ('registro', 'detalle_vehiculo', 'despacho_real')
    search_fields = ('detalle_vehiculo__transporte__chapa', 'registro__solicitud__id')