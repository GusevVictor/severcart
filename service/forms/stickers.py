# -*- coding:utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

class StickFormat(forms.Form):
    """Настройка формата печатаемых наклеек.
    """
    CHOICES = [('A4', 'A4'), ('A5', 'A5')]
    choice = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(), label=_('Select format'))
    required_css_class = 'required'

    def clean_choice(self):
        if not self.cleaned_data.get('choice', ''):
            raise forms.ValidationError('Value must be set')

        flag = False
        for paper_format in StickFormat.CHOICES:
            if self.cleaned_data.get('choice') == paper_format[0]:
                flag = True

        if not flag:
            raise forms.ValidationError('Value is invalid!')            

        return self.cleaned_data.get('choice')
