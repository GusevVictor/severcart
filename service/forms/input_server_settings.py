# -*- coding:utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

class SMTPsettings(forms.Form):
    """Ввод информации для подключению к SMTP серверу
    """
    smtp_server    = forms.CharField(label=_('Sever address'), widget=forms.TextInput(attrs={'class': 'inline left'}))
    smtp_port      = forms.IntegerField(label=_('Sever port'))
    email_sender   = forms.EmailField(label=_('Email sender'))
    smtp_login     = forms.CharField(label=_('SMTP login'), required=False)
    smtp_password  = forms.CharField(label=_('SMTP password'), max_length=32, widget=forms.PasswordInput, required=False)
    use_ssl        = forms.BooleanField(label=_('Use SSL'), required=False)
    use_tls        = forms.BooleanField(label=_('Use TLS'), required=False)

    required_css_class = 'required'

    def clean_smtp_port(self):
        """Проверяем введённый номер порта на область допустимых значений.
        """
        smtp_port = self.cleaned_data.get('smtp_port', 0)
        if (smtp_port >=1) and (smtp_port <= 65535):
            return smtp_port    
        else:
            raise forms.ValidationError(_('This port number is invalid'))


    def clean_smtp_login(self):
        """Очищаем логин пользователя от посторонних симолов.
        """
        smtp_login = self.cleaned_data.get('smtp_login', '')
        smtp_login = smtp_login.strip()
        smtp_login =  None if smtp_login == '' else smtp_login
        return smtp_login

    def clean_smtp_password(self):
        """Очищаем пароль пользователя от посторонних симолов.
        """
        smtp_password = self.cleaned_data.get('smtp_password', None)
        return smtp_password
