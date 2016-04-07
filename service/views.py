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
    if request.method == 'POST' and ('settings_email' in request.POST):
        form = SMTPsettings(request.POST)
        if form.is_valid():
            data_in_post   = form.cleaned_data
            smtp_server    = data_in_post['smtp_server']
            smtp_port      = data_in_post['smtp_port']
            email_sender   = data_in_post['email_sender']
            smtp_login     = data_in_post['smtp_login']
            smtp_password  = data_in_post['smtp_password']
            use_ssl        = data_in_post['use_ssl']

            # сохраняем введённые данные в настроечную таблицу
            conf = SevercartConfigs()
            conf.smtp_server    = smtp_server
            conf.smtp_port      = smtp_port
            conf.email_sender   = email_sender
            conf.smtp_login     = smtp_login
            conf.smtp_password  = smtp_password
            conf.use_ssl        = use_ssl
            conf.commit()
            messages.success(request, _('Settings successfully saved!') )
            return HttpResponseRedirect(request.path)
        else:
            context['form'] = form
    elif request.method == 'POST' and ('sender_email' in request.POST):
        sender_form = SendTestMail(request.POST)
        context['form'] = SMTPsettings()
        if sender_form.is_valid():
            send_message = _('Test email sender.')
            context['sender_form'] = sender_form
            context['send_message'] = send_message
        else:
            context['sender_form'] = sender_form

    elif request.method == 'GET':
        try:
            m1 = Settings.objects.get(pk=1)
        except Settings.DoesNotExist:
            form = SMTPsettings(initial={
                'smtp_server'   : '',
                'smtp_port'     : '',
                'email_sender'  : '',
                'smtp_login'    : '',
                'smtp_password' : '',
                'use_ssl'       : '',
            })
        else:
            # если таблица уже содержит данные, то инициализируем внутренние переменные
            form = SMTPsettings(initial={
                'smtp_server'   : m1.smtp_server,
                'smtp_port'     : m1.smtp_port,
                'email_sender'  : m1.email_sender,
                'smtp_login'    : m1.smtp_login,
                'smtp_password' : m1.smtp_password,
                'use_ssl'       : m1.use_ssl,
            })
            #
        sender_form = SendTestMail()
        context['form'] = form
        context['sender_form'] = sender_form
    else:
        context['error'] = _('Not implemented method.')
    return render(request, 'service/settings_mail.html', context)
