# -*- coding:utf-8 -*-
import time
import json
from django.http import JsonResponse, HttpResponse
from index.models import City, CartridgeItem, OrganizationUnits
from index.helpers import check_ajax_auth
from index.signals import sign_turf_cart

import logging
logger = logging.getLogger(__name__)

@check_ajax_auth
def city_list(request):
    """Возвращает список городов полученных из базы в ввиде json.
    """
    cites = City.objects.all()
    your_data = []
    tmp_dict = {}
    for elem in cites:
        tmp_dict[elem.id] = elem.city_name

    return JsonResponse(tmp_dict, safe=False)


def inx(request):
    """Пока заглушечка.
    """
    return HttpResponse('<h1>Api it works!</h1>')

@check_ajax_auth
def del_node(request):
    """Удаляем нод(у)(ы) из структуры организации
    """
    ar = request.POST.getlist('selected[]')
    ar = [int(i) for i in ar ]
    le = int(request.POST.get('len', ''))
    for ind in ar:
    	node = OrganizationUnits.objects.get(pk=ind)
    	node.delete()
    return HttpResponse('Data deleted!')


@check_ajax_auth
def turf_cartridge(request):
    """Безвозвратное удаление картриджа из БД. Списание расходника.
    """
    ar = request.POST.getlist('selected[]')
    ar = [int(i) for i in ar ]
    list_cplx = []
    for ind in ar:
        node = CartridgeItem.objects.get(pk=ind)
        list_cplx.append((node.id, str(node.cart_itm_name)))
        node.delete()

    sign_turf_cart.send(sender=None, list_cplx=list_cplx, request=request)

    return HttpResponse('Cartridjes deleted!')
