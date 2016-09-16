# -*- coding:utf-8 -*-
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from storages.models import Storages


class MoveItemsToStockWithBarCodeScanner(forms.Form):
    numbers = forms.CharField(widget=forms.HiddenInput(), required=False)

    number = forms.CharField(max_length = 256, required=False)

    storages = forms.ModelChoiceField(queryset=Storages.objects.filter(), label=_('Storage'))

    def clean_number(self):
        """Производим проверку строки на соответствие вида 4,5,6,7.
           Возвращает список из номеров РМ.
        """
        if not self.cleaned_data.get('numbers', ''):
            raise ValidationError(_('Required field.'))
        
        ret_list = self.cleaned_data.get('number', '')
        ret_list = ret_list.split(',')
        # преобразуем список строк в список айдишников
        tmp = list()
        for i in ret_list:
            try:
                i = int(i)
            except ValueError:
                i = 0
            
            tmp.append(i)
        
        ret_list = tmp
        return ret_list
