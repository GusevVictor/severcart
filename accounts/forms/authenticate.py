# -*- coding:utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

class AuthenticationForm(forms.Form):
    """Login form
    """
    username = forms.CharField(label=_('User name'), widget=forms.widgets.TextInput)
    password = forms.CharField(label=_('Password'), widget=forms.widgets.PasswordInput)

    class Meta:
        fields = ['username', 'password']
