# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from common.helpers import is_admin
from django.utils.translation import ugettext_lazy as _
from service.forms.input_server_settings import SMTPsettings
from service.forms.send_test_mail import SendTestMail
from service.helpers import SevercartConfigs


@login_required
@is_admin
def submenu(request):
    """
    """
    return render(request, 'service/submenu.html', context={})


@login_required
@is_admin
def settings_mail(request):
    """Форма настройки почтового ящика, с которого будут приходить уведомления
    """
    context = dict()
    context['sender_form']   = SendTestMail()
    conf = SevercartConfigs()
    context['settings_form'] = SMTPsettings(initial={
        'smtp_server'   : conf.smtp_server,
        'smtp_port'     : conf.smtp_port,
        'email_sender'  : conf.email_sender,
        'smtp_login'    : conf.smtp_login,
        'smtp_password' : conf.smtp_password,
        'use_ssl'       : conf.use_ssl,
        'use_tls'       : conf.use_tls,
    })
    return render(request, 'service/settings_mail.html', context)
