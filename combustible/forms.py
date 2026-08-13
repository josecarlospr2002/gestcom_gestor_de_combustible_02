from django import forms
from .models import CatalogoCliente


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