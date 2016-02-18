# -*- coding:utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from index.models import OrganizationUnits
from django.core.exceptions import ValidationError


class NoUse(forms.Form):
    org = forms.ModelChoiceField(queryset=OrganizationUnits.objects.root_nodes())
    
    OPTIONS = ((10, '10'), (20, '20'), (0, _('All over the past year')))
    
    diap = forms.ChoiceField(choices=OPTIONS)

    def clean_org(self):
        """
        """
        if not self.cleaned_data.get('org', ''):
            raise ValidationError(_('Required field.'))
        
        return self.cleaned_data.get('org', '')
  
    def clean_diap(self):
        """
        """
        diap_post = self.cleaned_data.get('diap', '')
        if not diap_post:
            raise ValidationError(_('Required field.'))
        
        diap_post = int(diap_post)        
        if not(diap_post == 10 or diap_post == 20 or diap_post == 0):
            raise ValidationError(_('Transferred to invalid values.'))
        
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
            raise ValidationError(_('You have entered incorrect data.'))
        if temp_count <= 0:
            raise ValidationError(_('The value must be greater than zero.'))
        if not temp_count:
            raise ValidationError(_('Field cannot be empty.'))
        return self.cleaned_data.get('cont', '')

    def clean_org(self):
        """
        """
        if not self.cleaned_data.get('org', ''):
            raise ValidationError(_('Required field.'))
        return self.cleaned_data.get('org', '')

class UsersCartridges(forms.Form):
    org = forms.ModelChoiceField(queryset=OrganizationUnits.objects.root_nodes(), required=True, label=_('Organization unit'))

    start_date = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'datepicker', 'readonly':'readonly'}), label=_('Start date'))

    required_css_class = 'required'
