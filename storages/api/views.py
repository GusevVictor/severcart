# -*- coding:utf-8 -*-

from django.http import JsonResponse
from django.utils.translation import ugettext as _
from django.db.models import Q
from storages.models import Storages
from index.models import CartridgeItem
from index.helpers import check_ajax_auth
from common.helpers import is_admin

import logging
logger = logging.getLogger(__name__)

@is_admin
@check_ajax_auth
def set_default(request):
    """Устанавливаем склад по умолчанию.
    """
    if request.method != 'POST':
        return HttpResponse('<h1>' + _('Only use POST requests!') + '</h1>')
    
    ansver = dict()
    select = request.POST.get('select', 0)
    try:
        select = int(select)
    except ValueError:
        select = 0
    try:
        m1 = Storages.objects.get(pk=select)
    except Storages.DoesNotExist:
        ansver['error'] = 1
        ansver['text'] = _('Storage does not exist.')

    # Производим дополнительную проверку. Департамент пользователя
    # должен быть равен департаменту склада.
    u_dept_id = request.user.departament.pk
    s_dept_id = m1.departament.pk

    if u_dept_id == s_dept_id:
        m2 = Storages.objects.filter(Q(default=True) & Q(departament=request.user.departament))
        for elem in m2:
            elem.default = False
            elem.save()
        m1.default = True
        m1.save()
        ansver['error'] = 0
        ansver['text'] = _('Set default is successfully.')
    else:
        ansver['error'] = 1
        ansver['text'] = _('Security error.')
    return JsonResponse(ansver)

@is_admin
@check_ajax_auth
def del_s(request):
    """Удаление склада.
    """
    if request.method != 'POST':
        return HttpResponse('<h1>' + _('Only use POST requests!') + '</h1>')
    
    ansver = dict()
    select = request.POST.get('select', 0)
    try:
        select = int(select)
    except ValueError:
        select = 0
    try:
        m1 = Storages.objects.get(pk=select)
    except Storages.DoesNotExist:
        ansver['error'] = 1
        ansver['text'] = _('Storage does not exist.')

    # Производим дополнительную проверку. Департамент пользователя
    # должен быть равен департаменту склада.
    u_dept_id = request.user.departament.pk
    s_dept_id = m1.departament.pk

    if u_dept_id == s_dept_id:
        # выполняем дополнительную проверку. Количество картриджей на складе 
        # должно быть равно нулю, иначе ошибка
        cart_count_in_stor = CartridgeItem.objects.filter(departament=u_dept_id).filter(sklad=m1.pk).count()
        if cart_count_in_stor == 0:
            m1.delete()
            ansver['error'] = 0
            ansver['text'] = _('Storage successfully deleted.')
        else:
            # если на складе есть расходники, выдаём сообщение об ошибке
            ansver['error'] = 1
            ansver['text'] = _('Storage can not be removed. It has a cartridges.')
    else:
        ansver['error'] = 1
        ansver['text'] = _('Security error.')

    return JsonResponse(ansver)
