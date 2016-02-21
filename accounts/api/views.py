# -*- coding:utf-8 -*-

from django.shortcuts import render
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from accounts.models import AnconUser
from index.helpers import check_ajax_auth

@check_ajax_auth
def del_users(request):
    """
    """
    resp_dict = dict()
    ar = request.POST.get('selected')
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
