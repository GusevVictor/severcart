# -*- coding:utf-8 -*-
import time
import json
from django.http import JsonResponse, HttpResponse
from index.models import City, CartridgeItem, OrganizationUnits
from index.helpers import check_ajax_auth
from index.signals import sign_turf_cart, sign_add_full_to_stock
from index.forms.add_items import AddItems

import logging
logger = logging.getLogger(__name__)


@check_ajax_auth
def ajax_add_cart_items(request):
    """Довляем новые картриджи на склад через Аякс
    """
    if request.method != 'POST':
        return HttpResponse('<h1>Only use POST requests!</h1>')    
    form = AddItems(request.POST)
    if form.is_valid():
        data_in_post = form.cleaned_data
        cart_name_id = data_in_post.get('cartName')
        cart_doc     = data_in_post.get('doc')
        request.session['']

    else:
        #form.errors
        pass
    return HttpResponse('<h1>AJAX it works!</h1>')

    last_num     = CartridgeItem.objects.filter(departament=request.user.departament).order_by('-cart_number')
    if last_num:
        last_num = last_num[0].cart_number
    else:
        last_num = 0
    cart_number  = last_num + 1
    # получаем объект текущего пользователя
    list_cplx = []
    with transaction.atomic():
        for i in range(count_items):
            m1 = CartridgeItem(cart_number=cart_number,
                               cart_itm_name=data_in_post['cartName'],
                               cart_date_added=timezone.now(),
                               cart_date_change=timezone.now(),
                               cart_number_refills=0,
                               departament=request.user.departament,
                               delivery_doc=doc_id,
                               )
            m1.save()
            list_cplx.append((m1.id, m1.cart_number, cart_type))
            cart_number += 1
    
    if count_items == 1:
        tmpl_message = 'Расходник %s успешно добавлен.'
    elif count_items > 1:
        tmpl_message = 'Расходники %s успешно добавлены.'
    
    sign_add_full_to_stock.send(sender=None, list_cplx=list_cplx, request=request)


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
        list_cplx.append((node.id, str(node.cart_itm_name), node.cart_number))
        node.delete()

    sign_turf_cart.send(sender=None, list_cplx=list_cplx, request=request)

    return HttpResponse('Cartridjes deleted!')
