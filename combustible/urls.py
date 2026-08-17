from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),

    # URLs de Catálogo de Cliente
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/crear/', views.crear_cliente, name='crear_cliente'),
    path('clientes/editar/<int:pk>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/ver/<int:pk>/', views.ver_cliente, name='ver_cliente'),

    # URLs de Transporte
    path('transporte/', views.lista_transporte, name='lista_transporte'),
    path('transporte/crear/', views.crear_vehiculo, name='crear_vehiculo'),
    path('transporte/editar/<int:pk>/', views.editar_vehiculo, name='editar_vehiculo'),
    path('transporte/eliminar/<int:pk>/', views.eliminar_vehiculo, name='eliminar_vehiculo'),

    # URLs de Solicitudes
    path('solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),
    path('solicitudes/crear/', views.crear_solicitud, name='crear_solicitud'),
    path('solicitudes/ver/<int:pk>/', views.ver_solicitud, name='ver_solicitud'),
    path('solicitudes/editar/<int:pk>/', views.editar_solicitud, name='editar_solicitud'),
    path('solicitudes/enviar/<int:pk>/', views.enviar_solicitud, name='enviar_solicitud'),
    path('solicitudes/eliminar/<int:pk>/', views.eliminar_solicitud, name='eliminar_solicitud'),
    path('solicitudes/aprobar/<int:pk>/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('solicitudes/rechazar/<int:pk>/', views.rechazar_solicitud, name='rechazar_solicitud'),
]
