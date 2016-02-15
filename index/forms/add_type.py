# -*- coding:utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from index.models import CartridgeType


class AddCartridgeType(ModelForm):
    required_css_class = 'required'
    cart_type = forms.CharField(error_messages={'required' : _('Required field.')}, label=_('Type consumables'))
    
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
        data = self.cleaned_data.get('cart_type').strip()
        if self.update:
            return data
        else:
            search_type = CartridgeType.objects.filter(cart_type=data)
            if search_type:
                raise forms.ValidationError(_('This name already exists!'))            
            else:
                return data

    def clean_comment(self):
        """Проверяет, что длина комментария не превышает допустимой длины.
        """
        if len(self.cleaned_data['comment']) > 161:
            raise forms.ValidationError(_('You have exceeded the maximum number of characters. No more than 160.'))
        return self.cleaned_data['comment'].strip()
