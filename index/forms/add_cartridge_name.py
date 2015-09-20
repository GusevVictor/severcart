from django.forms import ModelForm
from index.models import CartridgeItemName


class AddCartridgeName(ModelForm):
    class Meta:
        model = CartridgeItemName
        fields = ['cart_itm_name', 'cart_itm_type']
