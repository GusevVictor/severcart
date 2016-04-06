# -*- coding:utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

class SMTPsettings(forms.Form):
    """Ввод информации для подключению к SMTP серверу
    """
    server_address = forms.CharField(label=_('Sever address'))
    server_port    = forms.IntegerField(label=_('Sever port'))
    email_sender   = forms.EmailField(label=_('Email sender'))
    smtp_login     = forms.CharField(label=_('SMTP login'))
    smtp_password  = forms.CharField(label=_('SMTP password'), widget=forms.PasswordInput)
    use_ssl        = forms.BooleanField(label=_('Use SSL'), required=False)

    required_css_class = 'required'
    
    #def user_id_clean(self):
        
