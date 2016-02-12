# -*- coding:utf-8 -*-

from index.models import FirmTonerRefill, City
from django import forms

class FirmTonerRefillF(forms.Form):
    firm_name     = forms.CharField(required=True, error_messages={'required': 'Поле обязательно для заполнения.'}, label='Название')
    firm_city     = forms.ModelChoiceField(queryset=City.objects.all(), 
                                            error_messages={'required': 'Поле обязательно для заполнения.'}, 
                                            required=True,
                                            label='Город',)
    firm_contacts = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 15}), label='Контакты', required=False)
    firm_address  = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 15}), label='Адрес', required=False)
    firm_comments = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'cols': 15}), label='Коментарии', required=False)
    
    required_css_class = 'required'
