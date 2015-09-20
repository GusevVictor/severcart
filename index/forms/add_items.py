from django import forms
from index.models import CartridgeItemName


class AddItems(forms.Form):
    cart_name = forms.ModelChoiceField(queryset=CartridgeItemName.objects.all(), empty_label=' ')
    cart_count = forms.IntegerField(min_value=0)