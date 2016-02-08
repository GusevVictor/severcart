# -*- coding:utf-8 -*-

import time
import json
from django.http import JsonResponse, HttpResponse
from django.db.models.deletion import ProtectedError
from index.models import CartridgeItemName, CartridgeType
from index.helpers import check_ajax_auth


import logging
logger = logging.getLogger(__name__)

@check_ajax_auth
def del_cart_name(request):
    """Удаляем имя расходного материала через аякс
    """
    if request.method != 'POST':
        return HttpResponse('<h1>Only use POST requests!</h1>')    
    
    resp_dict = dict()
    cart_name_id = request.POST.get('cart_name_id', '')
    atype = request.POST.get('atype', '')

    try:
        cart_name_id = int(cart_name_id)
    except ValueError:
        cart_name_id = 0

    if atype == 'cart_name':
        try:
            m1 = CartridgeItemName.objects.get(pk=cart_name_id)
        except CartridgeItemName.DoesNotExist:
            resp_dict['error'] = '1'
            resp_dict['text']  = 'Объект с таким ID не найден.'
        try:
            m1.delete()
        except ProtectedError:
            resp_dict['error'] = '1'
            resp_dict['text']  = 'Имя удалить невозможно, т. к. на него ссылаются другие объекты.'    
        else:
            resp_dict['error'] = '0'
            resp_dict['text']  = 'Имя успешно удалено.'
    elif atype == 'cart_type':
        try:
            m1 = CartridgeType.objects.get(pk=cart_name_id)
        except CartridgeType.DoesNotExist:
            resp_dict['error'] = '1'
            resp_dict['text']  = 'Объект с таким ID не найден.'
        try:
            m1.delete()
        except ProtectedError:
            resp_dict['error'] = '1'
            resp_dict['text']  = 'Тип удалить невозможно, т. к. на него ссылаются другие объекты.'    
        else:
            resp_dict['error'] = '0'
            resp_dict['text']  = 'Имя успешно удалено.'
    return JsonResponse(resp_dict, safe=False)
