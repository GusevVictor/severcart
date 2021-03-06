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
def general_settings(request):
    """Вывод формы настройки отрисовки наклеек.
    """
    context = {}
    conf = SevercartConfigs()

    if request.method == 'POST':
        form = StickFormat(request.POST)
        if form.is_valid():
            data_in_post = form.cleaned_data
            choice = data_in_post.get('choice','A4')
            print_qr_code = data_in_post.get('print_qr_code')
            time_zone = data_in_post.get('time_zone')
            show_time = data_in_post.get('show_time')
            conf.page_format = choice
            conf.print_bar_code = print_qr_code
            conf.time_zone = time_zone
            conf.show_time = show_time
            conf.commit()
            context['form'] = form
            messages.success(request, _('Settings success saved.'))
        else:
            context['form'] = form
    else:
        print_qr_code = 1 if conf.print_bar_code else 2
        show_time     = 1 if conf.show_time else 2
        form = StickFormat(initial={'choice': conf.page_format,
                                    'print_qr_code': print_qr_code, # Внимание! Есть соблазнзаменить на self.print_qr_code
                                    'time_zone': conf.time_zone,
                                    'show_time': show_time,
                                    })
        context['form'] = form
    return render(request, 'service/general_settings.html', context)
