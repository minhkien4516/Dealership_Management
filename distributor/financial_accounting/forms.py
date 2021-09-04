from django import forms

from financial_accounting.models import Importation


class ImportationForm(forms.ModelForm):
    payed = forms.IntegerField(min_value=1, label='Thanh toán')

    class Meta:
        model = Importation
        fields = ('payed',)