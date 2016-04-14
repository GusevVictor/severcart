# -*- coding:utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

class SendMail(forms.Form):
    """Отправка тестового письма для проверки настроек 
       почтового сервера.
    """
    email   = forms.EmailField(label=_('Email recipient'))
    required_css_class = 'required'
