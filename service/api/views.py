# -*- coding:utf-8 -*-

from django.shortcuts import render
from django.conf import settings
from django.utils.translation import ugettext as _
from django.http import HttpResponse, JsonResponse
from index.helpers import check_ajax_auth
from service.helpers import SevercartConfigs
from service.forms.input_server_settings import SMTPsettings

@check_ajax_auth
def send_test_email(request):
    """
    """
    resp_dict = dict()
    text  = request.POST.get('text')
    email = request.POST.get('email')

    return JsonResponse(resp_dict)
    try:
        ar = int(ar)
    except ValueError:
        HttpResponse(_('Error in data processing'), status=501)
    
    usr_name = ''
    if request.user.id == ar:
        resp_dict['error'] = '1'
        resp_dict['text']  = _('User %(user_name)s can not be deleted') % {'user_name': request.user}
        return JsonResponse(resp_dict)
    
    try:
        usr = AnconUser.objects.get(pk=ar)
    except AnconUser.DoesNotExist: 
        resp_dict['error'] = '1'
        resp_dict['text']  = _('Object not found')
        return JsonResponse(resp_dict)
    else:
        if settings.DEMO:
            resp_dict['error'] = '1'
            resp_dict['text']  = _('In DEMO users not delete!')
            return JsonResponse(resp_dict)
        usr_name = usr.username
        usr.delete()
        resp_dict['error'] = '0'
        resp_dict['text']  = _('User %(user_name)s was successfully deleted') % {'user_name': usr_name}
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
