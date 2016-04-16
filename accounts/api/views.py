# -*- coding:utf-8 -*-

from django.conf import settings
from django.utils.translation import ugettext as _
from django.http import HttpResponse, JsonResponse
from django.utils.crypto import get_random_string
from accounts.models import AnconUser
from index.helpers import check_ajax_auth
from accounts.forms.send_email import SendMail
from service.helpers import send_email


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

def send_repair_email(request):
    """API функция по отправке эл. писем для восстановления 
       забытого пароля.
    """
    resp_dict = dict()
    resp_dict['errors'] = ''
    form = SendMail(request.POST)
    if form.is_valid():
        data_in_post = form.cleaned_data
        email = data_in_post.get('email', '')
        obj = AnconUser.objects.filter(email=email)
        if not obj:
            resp_dict['errors'] = _('Email was not found.')
            return JsonResponse(resp_dict)

        if len(obj) > 1:
            resp_dict['errors'] = _('Email should not be repeated for different users.')
            return JsonResponse(resp_dict)

        title = _('Forgotten password recovery')
        # Генерируем случайную буквенно цифорвую последовательность
        chars = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        secret_key = get_random_string(64, chars)
        # сохраняем ключ в объекте пользователя
        user_obj = AnconUser.objects.get(email=email)
        user_obj.secret_key = secret_key
        user_obj.save()
        domain = request.get_host()
        text = """
        Для восстановления забытого пароля перейдите по ссылке http://%s/manage_users/recover_password/%s
        """ 
        text = text % (domain, secret_key, )
        try:
            send_email(reciver=email, title=title, text=text)
        except Exception as e:
            resp_dict['errors'] =str(e)
        else:
            resp_dict['text'] = _('Mail successfully sended!')
    else:
        # если форма содержит ошибки, то сообщаем о них пользователю.
        error_message = dict([(key, [error for error in value]) for key, value in form.errors.items()])
        resp_dict['errors'] = error_message
    
    return JsonResponse(resp_dict)
