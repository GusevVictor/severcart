from django.shortcuts import render
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
        HttpResponse('Ошибка в обработке данных.', status=501)
    
    usr_name = ''
    usrs_name = []
    for ind in ar:
        try:
            usr = AnconUser.objects.get(pk=ind)
        except ObjectDoesNotExist: 
            HttpResponse('Объект не найден.', status=501)        
        else:
            usr_name = usr.username
            usrs_name.append(usr_name)
            usr.delete()

    usrs_name = [str(elem) for elem in usrs_name]
    usrs_name = ', '.join(usrs_name)
    if len(ar) == 1:
        return JsonResponse({'msg': 'Пользователь %s успешно удалён.' % (usr_name, ) })
    else:
        return JsonResponse({'msg': 'Пользователи %s успешно удалёны.' % (usrs_name, )})
    