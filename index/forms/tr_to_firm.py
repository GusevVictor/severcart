# -*- coding:utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from index.models import CartridgeItemName, FirmTonerRefill
from docs.models  import SCDoc
from django.db.models import Q

class TransfeToFirm(forms.Form):
    numbers = forms.CharField(widget=forms.HiddenInput(), required=True)
    
    firms = forms.ModelChoiceField(queryset=FirmTonerRefill.objects.all(),
                                    error_messages={'required': _('Required field.')},
                                    empty_label='',
                                    required=True,
                                  )

    doc   = forms.ModelChoiceField(queryset=SCDoc.objects.filter(), required=False)

    price = forms.IntegerField(required=False) 

    required_css_class = 'required'


    def clean_numbers(self):
        """Производим проверку строки на соответствие вида 4,5,6,7.
           Возвращает список из номеров картриджей.
        """
        if not self.cleaned_data.get('numbers', ''):
            raise ValidationError(_('Required field.'))
        
        ret_list = self.cleaned_data.get('numbers', '')
        ret_list = ret_list.split(',')
        return ret_list

    def clean_price(self):
        """
        """
        price = self.cleaned_data.get('price', 0)
        try:
            price = int(price)
        except ValueError:
            raise ValidationError(_('You have entered the wrong data.'))

        if price <= 0:
            raise ValidationError(_('The value must be greater than zero.'))

        return self.cleaned_data.get('price', '')

    def clean_doc(self):
        """
        """
        if not self.cleaned_data.get('doc', ''):
            return None
        doc_id = self.cleaned_data.get('doc', '')
        return doc_id.pk
