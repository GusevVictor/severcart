# -*- coding:utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

class ChangePassword(forms.Form):
    """Форма смены пароля.
    """
    password1 = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    password2 = forms.CharField(widget=forms.PasswordInput, label=_('Password again'))

    required_css_class = 'required'

    def clean(self):
        """Verifies that the values entered into the password fields match
        """
        # вызывает ошибку дублирования логина
        if ( 'password1' in self.cleaned_data ) and ( 'password2' in self.cleaned_data ): 
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_('Passwords do not match. Please enter them again'))
        return self.cleaned_data
