from django import forms
from django.core.validators import MinValueValidator
from .models import CatalogoCliente, Transporte, ModeloSolicitud, SuministroCombustible


class CatalogoClienteForm(forms.ModelForm):
    class Meta:
        model = CatalogoCliente
        fields = ['cliente', 'clasificacion', 'no_contrato']
        widgets = {
            'cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del cliente'
            }),
            'clasificacion': forms.Select(attrs={
                'class': 'form-control',
            }),
            'no_contrato': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el número de contrato',
            }),
        }
        labels = {
            'cliente': 'Cliente',
            'clasificacion': 'Clasificación',
            'no_contrato': 'No. Contrato',
        }

    def clean_cliente(self):
        cliente = self.cleaned_data.get('cliente')
        if cliente:
            cliente_normalizado = ' '.join(cliente.strip().split()).lower()
            existe = CatalogoCliente.objects.filter(cliente__iexact=cliente_normalizado)
            if self.instance.pk:
                existe = existe.exclude(pk=self.instance.pk)
            if existe.exists():
                raise forms.ValidationError('Este cliente ya existe en el catálogo.')
        return cliente

    def clean(self):
        cleaned_data = super().clean()
        clasificacion = cleaned_data.get('clasificacion')
        no_contrato = cleaned_data.get('no_contrato')

        if clasificacion == 'consumo':
            if no_contrato:
                self.add_error('no_contrato', 'Los clientes de Consumo no deben tener número de contrato.')
        else:
            if not no_contrato:
                self.add_error('no_contrato', 'El número de contrato es obligatorio para esta clasificación.')

        return cleaned_data


class TransporteForm(forms.ModelForm):
    class Meta:
        model = Transporte
        fields = ['cliente', 'tipo_vehiculo', 'chapa', 'ic']
        widgets = {
            'cliente': forms.Select(attrs={
                'class': 'form-control',
            }),
            'tipo_vehiculo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el tipo de vehículo'
            }),
            'chapa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese la chapa'
            }),
            'ic': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
        }
        labels = {
            'cliente': 'Cliente',
            'tipo_vehiculo': 'Tipo de Vehículo',
            'chapa': 'Chapa',
            'ic': 'I/C',
        }


class ModeloSolicitudForm(forms.ModelForm):
    class Meta:
        model = ModeloSolicitud
        fields = ['fecha_hora']
        widgets = {
            'fecha_hora': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
        }
        labels = {
            'fecha_hora': 'Fecha y Hora',
        }

    def clean_fecha_hora(self):
        fecha_hora = self.cleaned_data.get('fecha_hora')
        if fecha_hora:
            from django.utils import timezone
            if timezone.is_naive(fecha_hora):
                fecha_hora = timezone.make_aware(fecha_hora)
            if fecha_hora > timezone.now():
                raise forms.ValidationError('No se puede registrar una solicitud con fecha futura.')
        return fecha_hora


class SuministroCombustibleForm(forms.ModelForm):
    class Meta:
        model = SuministroCombustible
        fields = ['fecha_hora', 'cantidad', 'descripcion']
        widgets = {
            'fecha_hora': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Opcional: descripción o nota',
                'rows': '3',
            }),
        }
        labels = {
            'fecha_hora': 'Fecha y Hora',
            'cantidad': 'Cantidad a Insertar',
            'descripcion': 'Descripción / Nota',
        }

    def clean_fecha_hora(self):
        fecha_hora = self.cleaned_data.get('fecha_hora')
        if fecha_hora:
            from django.utils import timezone
            if timezone.is_naive(fecha_hora):
                fecha_hora = timezone.make_aware(fecha_hora)
            if fecha_hora > timezone.now():
                raise forms.ValidationError('No se puede registrar un suministro con fecha futura.')
        return fecha_hora

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is not None and cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor que 0.')
        return cantidad
