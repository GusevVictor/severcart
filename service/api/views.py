# -*- coding:utf-8 -*-

from django.shortcuts import render
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.core.mail.backends.smtp import EmailBackend
from index.helpers import check_ajax_auth
from service.helpers import SevercartConfigs
from service.forms.input_server_settings import SMTPsettings
from service.forms.send_test_mail import SendTestMail


@check_ajax_auth
def send_test_email(request):
    """
    """
    resp_dict = dict()
    errors        = list()
    text  = request.POST.get('text')
    email = request.POST.get('email')
    form = SendTestMail(request.POST)
    if form.is_valid():
        data_in_post = form.cleaned_data
        resp_dict['errors'] = ''
        mconf         = SevercartConfigs()
        subject       = text.strip()
        message       = text.strip()
        from_email    = mconf.email_sender
        to_email      = email
        auth_user     = mconf.smtp_login
        auth_password = mconf.smtp_password
        connection    = EmailBackend(
                            host = mconf.smtp_server,
                            port = mconf.smtp_port,
                            username=mconf.smtp_login,
                            password=mconf.smtp_password,
                            use_tls=True
                        )
        try:
            send_mail(subject, 
                      message, 
                      from_email, 
                      [to_email], 
                      connection=connection)
        except Exception as e:
            resp_dict['errors'] =str(e)
            

    else:
        # если форма содержит ошибки, то сообщаем о них пользователю.
        error_message = dict([(key, [error for error in value]) for key, value in form.errors.items()])
        resp_dict['errors'] = error_message
    
    return JsonResponse(resp_dict)


@check_ajax_auth
def settings_email(request):
    """
    """
    resp_dict     = dict()
    errors        = list()
    form = SMTPsettings(request.POST)
    if form.is_valid():
        data_in_post = form.cleaned_data
        mconf = SevercartConfigs()
        mconf.smtp_server   = data_in_post['smtp_server']
        mconf.smtp_port     = data_in_post['smtp_port']
        mconf.email_sender  = data_in_post['email_sender']
        mconf.smtp_login    = data_in_post['smtp_login']
        mconf.smtp_password = data_in_post['smtp_password']
        mconf.use_ssl       = data_in_post['use_ssl']
        mconf.commit()
        resp_dict['errors'] = ''
        resp_dict['text']   = _('Settings successfully saved.')
    else:
        error_message = dict([(key, [error for error in value]) for key, value in form.errors.items()])
        resp_dict['errors'] = error_message
    
    return JsonResponse(resp_dict)
