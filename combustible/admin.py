from django.contrib import admin
from .models import CatalogoCliente


@admin.register(CatalogoCliente)
class CatalogoClienteAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'clasificacion', 'no_contrato')
    list_filter = ('clasificacion',)
    search_fields = ('cliente', 'no_contrato')