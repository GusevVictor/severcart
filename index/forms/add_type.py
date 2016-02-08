# -*- coding:utf-8 -*-

from django import forms
from django.forms import ModelForm
from index.models import CartridgeType


class AddCartridgeType(ModelForm):
    required_css_class = 'required'
    cart_type = forms.CharField(error_messages={'required' : 'Поле обязательно для заполнения.'}, label='Тип расходного материала')
    
    class Meta:
        model = CartridgeType
        fields = ['cart_type', 'comment']

    def __init__(self, *args, **kwargs):
        """http://stackoverflow.com/questions/1202839/get-request-data-in-django-form
        """
        self.update = kwargs.pop('update')
        super(AddCartridgeType, self).__init__(*args, **kwargs)
        
    def clean_cart_type(self):
        """проверяем данные на наличие дублей.
        """
        data = self.cleaned_data.get('cart_type').strip().lower()
        if self.update:
            return data
        else:
            search_type = CartridgeType.objects.filter(cart_type=data)
            if search_type:
                raise forms.ValidationError('Данное наменование уже существует!')            
            else:
                return data

    def clean_comment(self):
        """Проверяет, что длина комментария не превышает допустимой длины.
        """
        if len(self.cleaned_data['comment']) > 161:
            raise forms.ValidationError('Превышено максимальное количество символов. Допустимо не более 160.')
        return self.cleaned_data['comment'].strip()
