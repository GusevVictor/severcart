# -*- coding:utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from docs.models  import SCDoc


class FromFirmToStock(forms.Form):

    doc = forms.ModelChoiceField(queryset=SCDoc.objects.filter(), required=False)

    def clean_doc(self):
        """
        """
        if not self.cleaned_data.get('doc', ''):
            return None
        return self.cleaned_data.get('doc', '')
