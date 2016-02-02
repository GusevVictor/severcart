# -*- coding:utf-8 -*-

from django import forms
from index.models import OrganizationUnits


class NoUse(forms.Form):
    org = forms.ModelChoiceField(queryset=OrganizationUnits.objects.root_nodes(), required=True, label='Организация')
    OPTIONS = (
                ('MON', 'Месяц'),
                ('QAR', 'Квариал'),
                ('YEA', 'Год'),
                ('ALL', 'За всё время'),
            )
    diap = forms.ChoiceField(choices=OPTIONS, label='Диапазон', required=True)

    def clean_org(self):
        """
        """
        return self.cleaned_data.get('org', '')
  
    def clean_diap(self):
        """
        """
        return self.cleaned_data.get('diap', '')
