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
