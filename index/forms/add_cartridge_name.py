from django import forms
from index.models import CartridgeItemName


class AddCartridgeName(forms.ModelForm):
    class Meta:
        model = CartridgeItemName
        fields = ['cart_itm_name', 'cart_itm_type']

    def clean_cart_itm_name(self):
        """проверяем данные на наличие дублей.
        """
        data = self.cleaned_data.get('cart_itm_name').strip().lower()
        search_type = CartridgeItemName.objects.filter(cart_itm_name=data)
        if search_type:
            raise forms.ValidationError('Данное наменование уже существует!')            
        else:
            return data
