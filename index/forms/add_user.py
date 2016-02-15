# -*- coding:utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from index.models import OrganizationUnits


class AddUser(forms.Form):
    last_name  = forms.CharField(label=_('Surname'))
    first_name = forms.CharField(label=_('Name'))
    patronymic = forms.CharField(label=_('Middle name'))
    username   = forms.CharField(label=_('Login'))
    password   = forms.CharField(label=_('Password'))
    department = forms.ModelChoiceField(label=_('Organization'), queryset=OrganizationUnits.objects.all(), empty_label=' ')
