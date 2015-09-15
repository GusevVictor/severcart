__author__ = 'User'
from django.forms import ModelForm
from index.models import CartridgeType


class AddCartridgeType(ModelForm):
    class Meta:
        model = CartridgeType
        fields = ['cart_type']




