# -*- coding:utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

class StickFormat(forms.Form):
    """Настройка формата печатаемых наклеек.
    """
    CHOICES = [('A4', 'A4'), ('A5', 'A5')]
    YES_NO  = [(1, _('Yes')), (2, _('No'))]
    choice = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(), label=_('Select paper format'))
    print_qr_code = forms.ChoiceField(choices=YES_NO, widget=forms.RadioSelect(), label=_('Print QR code?'))
    required_css_class = 'required'

    def clean_choice(self):
        if not self.cleaned_data.get('choice', ''):
            raise forms.ValidationError(_('Value must be set'))

        flag = False
        for paper_format in StickFormat.CHOICES:
            if self.cleaned_data.get('choice') == paper_format[0]:
                flag = True

        if not flag:
            raise forms.ValidationError('Value is invalid!')            

        return self.cleaned_data.get('choice')

    def clean_print_qr_code(self):
        if not self.cleaned_data.get('print_qr_code', 0):
            raise forms.ValidationError(_('Value must be set'))
        set_var = self.cleaned_data.get('print_qr_code')
        if set_var == '1':
            return True
        elif set_var == '2':
            return False
        else:
            raise forms.ValidationError(_('Invalid value'))
