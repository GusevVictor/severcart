# -*- coding:utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from index.models import CartridgeItemName, FirmTonerRefill
from docs.models  import SCDoc
from django.db.models import Q

class TransfeToFirm(forms.Form):
    numbers = forms.CharField(widget=forms.HiddenInput(), required=True)
    
    firm = forms.ModelChoiceField(queryset=FirmTonerRefill.objects.all(),
                                    error_messages={'required': _('Required field.')},
                                    empty_label='',
                                    required=True,
                                  )

    doc   = forms.ModelChoiceField(queryset=SCDoc.objects.filter(), required=False)

    price = forms.IntegerField(required=False) 

    def clean_numbers(self):
        """Производим проверку строки на соответствие вида 4,5,6,7.
           Возвращает список из номеров картриджей.
        """
        if not self.cleaned_data.get('numbers', ''):
            raise ValidationError(_('Required field.'))
        
        ret_list = self.cleaned_data.get('numbers', '')
        ret_list = ret_list.split(',')
        # преобразуем список строк в список айдишников
        tmp = list()
        for i in ret_list:
            try:
                i = int(i)
            except:
                i = 0
            
            tmp.append(i)
        
        ret_list = tmp
        return ret_list

    def clean_price(self):
        """Очищаем ценник от шелухи.
        """
        price = self.cleaned_data.get('price', 0)
        try:
            price = int(price)
        except:
            price = 0            

        if price < 0:
            raise ValidationError(_('The value must be greater than zero.'))

        return price

    def clean_doc(self):
        """
        """
        if not self.cleaned_data.get('doc', ''):
            return None
        doc_id = self.cleaned_data.get('doc', '')
        return doc_id.pk

    def clean_firm(self):
        """
        """
        if not self.cleaned_data.get('firm', ''):
            raise ValidationError(_('Required field.'))

        # TODO выполнить более продвинутую проверку на существование pk в СУБД
        firm = self.cleaned_data.get('firm')
        return firm.pk
