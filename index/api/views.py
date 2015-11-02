# -*- coding:utf-8 -*-
import time
import json
from django.http import JsonResponse, HttpResponse
from index.models import City, Summary, CartridgeItem, OrganizationUnits
from index.helpers import check_ajax_auth

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
def upd_dashboard_tbl(request):
	"""Освежаем модель Summary
	"""
	start_time = time.time()
	full_on_stock  = CartridgeItem.objects.filter(cart_owner__isnull=True).filter(cart_filled=True).count()
	empty_on_stock = CartridgeItem.objects.filter(filled_firm__isnull=True, 
                                        		  cart_owner__isnull=True,
                                        		  cart_filled=False,
                                        		 ).count()
	uses           = CartridgeItem.objects.filter(cart_owner__isnull=False).count()
	filled         = CartridgeItem.objects.filter(filled_firm__isnull=False).count()
	# TODO добавить фичу подсчёта кол-ва времени выполнения
	m1 = Summary.objects.get(pk=1)
	m1.full_on_stock  = full_on_stock
	m1.empty_on_stock = empty_on_stock
	m1.uses           = uses
	m1.filled         = filled
	m1.save()
	work_time = time.time() - start_time
	return HttpResponse(work_time)

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
    	#OrganizationUnits.objects.move_node(node, target=None)
    return HttpResponse('Data deleted!')
