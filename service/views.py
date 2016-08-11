# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from common.helpers import is_admin
from django.utils.translation import ugettext_lazy as _
from service.forms.input_server_settings import SMTPsettings
from service.forms.send_test_mail import SendTestMail
from service.forms.stickers import StickFormat
from service.helpers import SevercartConfigs


@never_cache
@login_required
@is_admin
def submenu(request):
    """
    """
    return render(request, 'service/submenu.html', context={})


@never_cache
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


@never_cache
@login_required
@is_admin
def stickers(request):
    """Вывод формы настройки отрисовки наклеек.
    """
    context = {}
    conf = SevercartConfigs()
    if request.method == 'POST':
        form = StickFormat(request.POST)
        if form.is_valid():
            data_in_post = form.cleaned_data
            choice = data_in_post.get('choice','A4')
            conf.page_format = choice
            conf.commit()
            context['form'] = form
            messages.success(request, _('Settings success saved.'))
        else:
            context['form'] = form    
    else:
        form = StickFormat(initial={'choice': conf.page_format})
        context['form'] = form
    return render(request, 'service/stickers.html', context)
