# -*- coding:utf-8 -*-

from django.utils.translation import ugettext as _
from django.http import JsonResponse
from index.helpers import check_ajax_auth
from service.forms.input_server_settings import SMTPsettings
from service.forms.send_test_mail import SendTestMail
from service.helpers import SevercartConfigs, send_email
from common.helpers import is_admin

@check_ajax_auth
@is_admin
def send_test_email(request):
    """
    """
    resp_dict = dict()
    form = SendTestMail(request.POST)
    if form.is_valid():
        data_in_post = form.cleaned_data
        email = data_in_post.get('email', '')
        text  = data_in_post.get('text', '')
        print(email, text)
        resp_dict['errors'] = ''
        try:
            send_email(reciver=email, title=text, text=text)
        except Exception as e:
            resp_dict['errors'] =str(e)
        else:
            resp_dict['text'] = _('Mail successfully sended!')
            
    else:
        # если форма содержит ошибки, то сообщаем о них пользователю.
        error_message = dict([(key, [error for error in value]) for key, value in form.errors.items()])
        resp_dict['errors'] = error_message
    
    return JsonResponse(resp_dict)


@check_ajax_auth
@is_admin
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
        mconf.use_tls       = data_in_post['use_tls']
        mconf.commit()
        resp_dict['errors'] = ''
        resp_dict['text']   = _('Settings successfully saved.')
    else:
        error_message = dict([(key, [error for error in value]) for key, value in form.errors.items()])
        resp_dict['errors'] = error_message
    
    return JsonResponse(resp_dict)
