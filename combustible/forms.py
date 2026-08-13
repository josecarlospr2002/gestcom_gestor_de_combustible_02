from django import forms
from django.core.validators import MinValueValidator
from .models import CatalogoCliente, Transporte


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
            # Normalizar: quitar espacios extras y convertir a minúsculas para comparar
            cliente_normalizado = ' '.join(cliente.strip().split()).lower()

            # Verificar si ya existe un cliente con ese nombre
            existe = CatalogoCliente.objects.filter(cliente__iexact=cliente_normalizado)

            # Si estamos editando, excluir el cliente actual
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
            # Si es Consumo, no debe tener número de contrato
            if no_contrato:
                self.add_error('no_contrato', 'Los clientes de Consumo no deben tener número de contrato.')
        else:
            # Si es Venta o Factura, debe tener número de contrato
            if not no_contrato:
                self.add_error('no_contrato', 'El número de contrato es obligatorio para esta clasificación.')

        return cleaned_data


class TransporteForm(forms.ModelForm):
    class Meta:
        model = Transporte
        fields = ['tipo_vehiculo', 'chapa', 'ic']
        widgets = {
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
            'tipo_vehiculo': 'Tipo de Vehículo',
            'chapa': 'Chapa',
            'ic': 'I/C',
        }

    def clean_ic(self):
        ic = self.cleaned_data.get('ic')
        if ic is not None and ic <= 0:
            raise forms.ValidationError('El I/C debe ser un número mayor que 0.')
        return ic

    def clean_chapa(self):
        chapa = self.cleaned_data.get('chapa')
        if chapa:
            # Normalizar: quitar espacios extras
            chapa_normalizado = ' '.join(chapa.strip().split())

            # Verificar si ya existe un vehículo con esa chapa
            existe = Transporte.objects.filter(chapa__iexact=chapa_normalizado)

            # Si estamos editando, excluir el vehículo actual
            if self.instance.pk:
                existe = existe.exclude(pk=self.instance.pk)

            if existe.exists():
                raise forms.ValidationError('Este vehículo ya existe en el registro.')

        return chapa