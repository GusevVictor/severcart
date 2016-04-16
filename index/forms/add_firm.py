# -*- coding:utf-8 -*-

from index.models import City
from django import forms
from django.utils.translation import ugettext_lazy as _

class FirmTonerRefillF(forms.Form):
    firm_name     = forms.CharField(required=True, error_messages={'required': _('Required field.')}, label=_('Name'))
    firm_city     = forms.ModelChoiceField(queryset=City.objects.all(), 
                                            error_messages={'required': _('Required field.')}, 
                                            required=True,
                                            label=_('Select city'),)
    firm_contacts = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 15}), label=_('Contacts'), required=False)
    firm_address  = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 15}), label=_('Address'), required=False)
    firm_comments = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'cols': 15}), label=_('Comments'), required=False)
    
    required_css_class = 'required'
