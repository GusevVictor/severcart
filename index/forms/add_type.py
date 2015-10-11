from django.forms import ModelForm
from index.models import CartridgeType


class AddCartridgeType(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = CartridgeType
        fields = ['cart_type']
