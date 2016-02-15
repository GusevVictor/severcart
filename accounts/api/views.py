# -*- coding:utf-8 -*-

from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from accounts.models import AnconUser
from index.helpers import check_ajax_auth

@check_ajax_auth
def del_users(request):
    """
    """
    ar = request.POST.getlist('selected[]')
    try:
        ar = [int(i) for i in ar ]
    except ValueError:

        HttpResponse(_('Error in data processing'), status=501)
    
    usr_name = ''
    usrs_name = []
    if request.user.id in ar:
        return HttpResponse(_('User %(user_name)s can not be deleted') % {'user_name': request.user}, status=501)        
    
    for ind in ar:
        try:
            usr = AnconUser.objects.get(pk=ind)
        except ObjectDoesNotExist: 
            return HttpResponse(_('Object not found'), status=501)        
        else:
            usr_name = usr.username
            usrs_name.append(usr_name)
            usr.delete()

    usrs_name = [str(elem) for elem in usrs_name]
    usrs_name = ', '.join(usrs_name)
    if len(ar) == 1:
        return JsonResponse({'msg': _('User %(user_name)s was successfully deleted') % {'user_name': usrs_name} })
    else:
        return JsonResponse({'msg': _('Users %(user_name)s was successfully deleted') % {'user_name': usrs_name} })
    