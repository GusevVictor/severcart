# -*- coding:utf-8 -*-

from django import forms


class AuthenticationForm(forms.Form):
    """
    Login form
    """
    username = forms.CharField(label='Имя пользователя', widget=forms.widgets.TextInput)
    password = forms.CharField(label='Пароль', widget=forms.widgets.PasswordInput)

    class Meta:
        fields = ['username', 'password']
