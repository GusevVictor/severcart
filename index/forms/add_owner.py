from django.forms import ModelForm
from index.models import CartridgeOwner


class AddCartridgeOwner(ModelForm):
    class Meta:
        model = CartridgeOwner
        fields = ['owner']
