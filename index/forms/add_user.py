# -*- coding:utf-8 -*-

from django import forms
from index.models import OrganizationUnits


class AddUser(forms.Form):
    last_name = forms.CharField(label='Фамилие')
    first_name = forms.CharField(label='Имя')
    patronymic = forms.CharField(label='Отчество')
    username = forms.CharField(label='Логин')
    password = forms.CharField(label='Пароль')
    department = forms.ModelChoiceField(label='Организация', queryset=OrganizationUnits.objects.all(), empty_label=' ')
