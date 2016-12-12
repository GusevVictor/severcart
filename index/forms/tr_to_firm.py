# -*- coding:utf-8 -*-
import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from index.models import FirmTonerRefill
from docs.models  import SCDoc


class TransfeToFirm(forms.Form):
    numbers = forms.CharField(widget=forms.HiddenInput(), required=True)
    
    firm = forms.ModelChoiceField(queryset=FirmTonerRefill.objects.all(),
                                    error_messages={'required': _('Required field.')},
                                    empty_label='',
                                    required=True,
                                    widget=forms.Select(attrs={'class':'load_doc_ajax'})
                                  )

    doc = forms.ModelChoiceField(queryset=SCDoc.objects.filter(), required=False)

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
            except ValueError:
                i = 0
            
            tmp.append(i)
        
        ret_list = tmp
        return ret_list

    # def clean_price(self):
    #     """Преобразуем цену в копейки/доллар центы/евро центры
    #     """
    #     price = self.cleaned_data.get('price', '')
    #     price = re.split('[\,\.]', price)
    #     try:
    #         price = [int(i) for i in price]
    #     except ValueError:
    #         price = 0

    #     if isinstance(price, list) and len(price) == 2:
    #         price = price[0]*100 + price[1]

    #     if isinstance(price, list) and len(price) == 1:
    #         price = price[0]*100

    #     if price < 0:
    #         raise ValidationError(_('The value must be greater than zero.'))

    #     return price

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

class TransfeToFirmScanner(forms.Form):
    """Форма передачи РМ в фоирму для облуживания. 
       Формируемый список РМ задаётся сканером штрих кодов.
    """
    #scan_number = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'readonly': True, 'class': 'barcode'}), required=True)
    scan_number = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'readonly': True, 'class': 'barcode'}), required=False)
    numbers = forms.CharField(widget=forms.HiddenInput(), required=True)
    
    firm = forms.ModelChoiceField(queryset=FirmTonerRefill.objects.all(),
                                    error_messages={'required': _('Required field.')},
                                    empty_label='',
                                    required=True,
                                  )

    doc = forms.ModelChoiceField(queryset=SCDoc.objects.filter(), required=False)

    #price = forms.CharField(required=False) 

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
            except ValueError:
                i = 0
            
            tmp.append(i)
        
        ret_list = tmp
        return ret_list

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
        try:
            firm = self.cleaned_data.get('firm')
        except:
            raise ValidationError(_('Firm object error.'))            
        return firm.pk
