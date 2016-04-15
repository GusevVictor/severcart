# -*- coding:utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

class StickFormat(forms.Form):
    """Настройка формата печатаемых наклеек.
    """
    CHOICES = [('A4', 'A4'), ('A5', 'A5')]
    choice = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(), label=_('Select format'))
    required_css_class = 'required'
