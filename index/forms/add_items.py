from django import forms
from index.models import CartridgeType


class AddItems(forms.Form):
    cart_name = forms.CharField(label='Название расходника', max_length=256)
    cart_type = forms.ModelChoiceField(queryset=CartridgeType.objects.all(), empty_label=None)
    cart_count = forms.IntegerField()
    cart_new = forms.BooleanField()
