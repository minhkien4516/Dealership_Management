from django import forms

from dealership.models import Dealership
from financial_accounting.models import ImportationDetailRequest
from .models import Exportation, ExportationDetail


class ImportationDetailForm(forms.ModelForm):
    product_price = forms.IntegerField(min_value=0, label='Giá nhập')
    product_quantity = forms.IntegerField(min_value=1, label='Số lượng')

    class Meta:
        model = ImportationDetailRequest
        fields = (
            'product_id',
            'product_name',
            'product_price',
            'product_quantity'
        )
        labels = {
            'product_id': 'Mã sản phẩm',
            'product_name': 'Tên sản phẩm',
        }


class MultipleImportationDetailForm(forms.Form):
    number = forms.IntegerField(min_value=2, max_value=10, label='Số lượng mặt hàng')


class ExportationForm(forms.ModelForm):
    class Meta:
        model = Exportation
        fields = ('payed', 'dealership')
        labels = {
            'payed': 'Thanh toán',
            'dealership': 'Đại lý'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dealership'].queryset = Dealership.objects.filter(is_active=True)


class ExportationDetailForm(forms.ModelForm):
    class Meta:
        model = ExportationDetail
        fields = (
            'product',
            'product_quantity'
        )
        labels = {
            'product': 'Sản phẩm',
            'product_quantity': 'Số lượng'
        }


class MultipleExportationDetailForm(forms.Form):
    number = forms.IntegerField(min_value=2, max_value=10)
