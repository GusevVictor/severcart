# -*- coding:utf-8 -*-

from django import forms
from django.forms import ModelForm
from index.models import CartridgeType


class AddCartridgeType(ModelForm):
    required_css_class = 'required'
    cart_type = forms.CharField(error_messages={'required' : 'Поле обязательно для заполнения.'}, label='Тип расходного материала')

    class Meta:
        model = CartridgeType
        fields = ['cart_type']

    def clean_cart_type(self):
        """проверяем данные на наличие дублей.
        """
        data = self.cleaned_data.get('cart_type').strip().lower()
        search_type = CartridgeType.objects.filter(cart_type=data)
        if search_type:
            raise forms.ValidationError('Данное наменование уже существует!')            
        else:
            return data
