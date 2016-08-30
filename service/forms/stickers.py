# -*- coding:utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

class StickFormat(forms.Form):
    """Настройка формата печатаемых наклеек.
    """
    CHOICES = [('A4', 'A4'), ('A5', 'A5')]
    YES_NO  = [(1, _('Yes')), (2, _('No'))]
    choice = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(), label=_('Select paper format'))
    print_bar_code = forms.ChoiceField(choices=YES_NO, widget=forms.RadioSelect(), label=_('Print bar code?'))
    print_name_obj = forms.ChoiceField(choices=YES_NO, widget=forms.RadioSelect(), label=_('Print name?'))
    print_name_ou  = forms.ChoiceField(choices=YES_NO, widget=forms.RadioSelect(), label=_('Print organizational unit name?'))

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

    def clean_print_bar_code(self):
        if not self.cleaned_data.get('print_bar_code', 0):
            raise forms.ValidationError(_('Value must be set'))
        set_var = self.cleaned_data.get('print_bar_code')
        if set_var == '1':
            return True
        elif set_var == '2':
            return False
        else:
            raise forms.ValidationError(_('Invalid value'))

    def clean_print_name_obj(self):
        if not self.cleaned_data.get('print_name_obj', 0):
            raise forms.ValidationError(_('Value must be set'))
        set_var = self.cleaned_data.get('print_name_obj')
        if set_var == '1':
            return True
        elif set_var == '2':
            return False
        else:
            raise forms.ValidationError(_('Invalid value'))

    def clean_print_name_ou(self):
        if not self.cleaned_data.get('print_name_ou', 0):
            raise forms.ValidationError(_('Value must be set'))
        set_var = self.cleaned_data.get('print_name_ou')
        if set_var == '1':
            return True
        elif set_var == '2':
            return False
        else:
            raise forms.ValidationError(_('Invalid value'))
