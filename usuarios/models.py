from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    DEPARTAMENTOS = [
        ('admin', 'Administrador del Sistema'),
        ('transporte', 'Departamento de Transporte'),
        ('petroleo', 'Departamento de Petróleo'),
        ('almacen', 'Almacén'),
        ('director', 'Director General'),
        ('director_aseguramiento', 'Director de Aseguramiento'),
        ('director_contabilidad', 'Director de Contab. y Finanzas'),
        ('director_produccion', 'Director de Producción'),
    ]

    departamento = models.CharField(
        max_length=30,
        choices=DEPARTAMENTOS,
        default='transporte',
        verbose_name='Departamento / Rol'
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.get_full_name()} - {self.get_departamento_display()}"