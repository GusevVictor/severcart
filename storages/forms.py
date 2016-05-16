# -*- coding:utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _


class AddStorage(forms.Form):
    """Создание новой единицы склада.
    """
    title       = forms.CharField(label=_('Title'))
    address     = forms.CharField(widget=forms.TextInput, label=_('Address'))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 15}), label=_('Description'))

    required_css_class = 'required'

    def clean_title(self):
        """
        """
        title = self.cleaned_data.get('title', '')
        if not title:
            raise forms.ValidationError(_('Requared field.'))
        return title


    def clean_address(self):
        """
        """
        address = self.cleaned_data.get('address', '')
        if not address:
            raise forms.ValidationError(_('Requared field.'))
        return address
