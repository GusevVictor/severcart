# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from common.helpers import is_admin
from django.utils.translation import ugettext_lazy as _
from .forms.input_server_settings import SMTPsettings
from .forms.send_test_mail import SendTestMail
from service.models import Settings
from .helpers import SevercartConfigs


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
    #context['settings_form'] = SMTPsettings()
    context['sender_form']   = SendTestMail()

    try:
        m1 = Settings.objects.get(pk=1)
    except Settings.DoesNotExist:
        context['settings_form'] = SMTPsettings(initial={
            'smtp_server'   : '',
            'smtp_port'     : '',
            'email_sender'  : '',
            'smtp_login'    : '',
            'smtp_password' : '',
            'use_ssl'       : '',
        })
    else:
        # если таблица уже содержит данные, то инициализируем внутренние переменные
        context['settings_form'] = SMTPsettings(initial={
            'smtp_server'   : m1.smtp_server,
            'smtp_port'     : m1.smtp_port,
            'email_sender'  : m1.email_sender,
            'smtp_login'    : m1.smtp_login,
            'smtp_password' : m1.smtp_password,
            'use_ssl'       : m1.use_ssl,
        })

    return render(request, 'service/settings_mail.html', context)
