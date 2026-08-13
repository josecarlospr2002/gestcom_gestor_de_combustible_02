from django.contrib import admin
from .models import CatalogoCliente, Transporte


@admin.register(CatalogoCliente)
class CatalogoClienteAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'clasificacion', 'no_contrato')
    list_filter = ('clasificacion',)
    search_fields = ('cliente', 'no_contrato')


@admin.register(Transporte)
class TransporteAdmin(admin.ModelAdmin):
    list_display = ('tipo_vehiculo', 'chapa', 'ic')
    search_fields = ('tipo_vehiculo', 'chapa')