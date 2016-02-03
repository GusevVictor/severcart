# -*- coding:utf-8 -*-

from django import forms
from index.models import OrganizationUnits
from django.core.exceptions import ValidationError


class NoUse(forms.Form):
    org = forms.ModelChoiceField(queryset=OrganizationUnits.objects.root_nodes())
    OPTIONS = ((10, '10'), (20, '20'), (0, 'Все за прошлые года'))
    diap = forms.ChoiceField(choices=OPTIONS)

    def clean_org(self):
        """
        """
        if not self.cleaned_data.get('org', ''):
            raise ValidationError('Поле обязательно для заполнения.')
        
        return self.cleaned_data.get('org', '')
  
    def clean_diap(self):
        """
        """
        diap_post = self.cleaned_data.get('diap', '')
        if not diap_post:
            raise ValidationError('Поле обязательно для заполнения.')
        
        diap_post = int(diap_post)        
        if not(diap_post == 10 or diap_post == 20 or diap_post == 0):
            raise ValidationError('Переданы недопустимые значения.')
        
        return diap_post

class Amortizing(forms.Form):
    org = forms.ModelChoiceField(queryset=OrganizationUnits.objects.root_nodes())

    cont = forms.CharField(max_length = 4, widget=forms.TextInput(attrs={'class': 'pm_counter', 
                                                                        'readonly': 'readonly',
                                                                        'data': '1'}))

    def clean_cont(self):
        """
        """
        temp_count = self.cleaned_data.get('cont', '')
        try:
            temp_count = int(temp_count)
        except ValueError:
            raise ValidationError("Вы ввели ошибочные данные.")
        if temp_count <= 0:
            raise ValidationError("Значение должно быть больше нуля.")
        if not temp_count:
            raise ValidationError("Поле не может быть пустым.")
        return self.cleaned_data.get('cont', '')

    def clean_org(self):
        """
        """
        if not self.cleaned_data.get('org', ''):
            raise ValidationError('Поле обязательно для заполнения.')
        return self.cleaned_data.get('org', '')
