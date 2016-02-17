# -*- coding:utf-8 -*-
import time
import json
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from common.helpers import is_admin
from index.models import ( City, 
                           CartridgeItem, 
                           OrganizationUnits, 
                           CartridgeItemName, 
                           FirmTonerRefill )
from index.helpers import check_ajax_auth
from index.signals import sign_turf_cart, sign_add_full_to_stock, sign_tr_empty_cart_to_stock
from index.forms.add_items import AddItems
from docs.models import SCDoc

import logging
logger = logging.getLogger(__name__)

@check_ajax_auth
def del_firm(request):
    """
    """
    if request.method != 'POST':
        return HttpResponse('<h1>' + _('Only use POST requests!') + '</h1>')

    resp_dict = dict()
    firm_id = request.POST.get('selected', '')
    if firm_id:
        try:
            firm_id = int(firm_id)
        except ValueError:
            firm_id = 0
    else:
        firm_id = 0

    try:
        firm = FirmTonerRefill.objects.get(pk=firm_id)
    except FirmTonerRefill.DoesNotExist:
        resp_dict['text']  = _('Firm not found')
        resp_dict['error'] = '1'
        return JsonResponse(resp_dict)
    else:
        firm.delete()
        resp_dict['text']  = _('Firm deleted!')
        resp_dict['error'] = '0'
    
    return JsonResponse(resp_dict)


@check_ajax_auth
def ajax_add_session_items(request):
    """Довляем новые картриджи на склад через Аякс
    """
    if request.method != 'POST':
        return HttpResponse('<h1>' + _('Only use POST requests!') + '</h1>')
    # если пришёл запрос то пополняем сессионную переменную
    # результаты отображаем на странице
    tmp_dict = dict()
    try:
        m1 = request.user.departament.pk
    except AttributeError:
        
        tmp_dict['mes']  = _('User not assosiate with organization unit!<br/>Error code: 101.')
        tmp_dict['error'] = '1'
        return JsonResponse(tmp_dict)
    tmp_dict['error'] = '0'
    form = AddItems(request.POST)
    if form.is_valid():
        data_in_post = form.cleaned_data
        cart_name_id = data_in_post.get('cartName').pk
        cart_name    = data_in_post.get('cartName').cart_itm_name
        cart_name    = str(cart_name)
        if data_in_post.get('doc'):
            cart_doc_id = data_in_post.get('doc')
        else:
            cart_doc_id = 0
        cart_count   = int(data_in_post.get('cartCount'))
        # Добавляем картриджи в БД
        last_num     = CartridgeItem.objects.filter(departament=request.user.departament).order_by('-cart_number')
        if last_num:
            last_num = last_num[0].cart_number
        else:
            last_num = 0
        cart_number  = last_num + 1
        # получаем объект текущего пользователя
        list_cplx = []
        with transaction.atomic():
            for i in range(cart_count):
                m1 = CartridgeItem(cart_number=cart_number,
                                   cart_itm_name=data_in_post.get('cartName'),
                                   cart_date_added=timezone.now(),
                                   cart_date_change=timezone.now(),
                                   cart_number_refills=0,
                                   departament=request.user.departament,
                                   delivery_doc=cart_doc_id,
                                   )
                m1.save()
                list_cplx.append((m1.id, cart_number, cart_name))
                cart_number += 1
        
        if cart_number == 1:
            tmpl_message = _('Cartridge successfully added.')
        elif cart_number > 1:
            tmpl_message = _('Cartridges successfully added.')

        # запускаем сигнал добавления событий
        sign_add_full_to_stock.send(sender=None, list_cplx=list_cplx, request=request)
        
        numbers = [ i[1] for i in list_cplx ] 
        # наполняем сессионную переменную cumulative_list
        tmp_list = [cart_name_id, cart_doc_id, numbers]
        if request.session.get('cumulative_list', False):
            # если в сессионной переменной уже что-то есть
            session_data = request.session.get('cumulative_list')
            session_data = json.loads(session_data)
            session_data.append(tmp_list)
            use2var = session_data
            session_data = json.dumps(session_data)
            # перезаписываем переменную в сессии новыми значениями
            request.session['cumulative_list'] = session_data
        else:
            # если сессионная added_list пуста
            use2var = [ tmp_list ]
            tmp_list = json.dumps(use2var)
            request.session['cumulative_list'] = tmp_list        
        # заполняем тупой кэш нужными данными названий картриджей и их айдишников, это минимизирует обращения к базу
        simple_cache = dict()
        list_names = CartridgeItemName.objects.all()
        for elem in list_names:
            simple_cache[elem.pk] = elem.cart_itm_name
        # формируем http ответ
        # формат  [ [name, title,  numbers=[1,2,3,4]] ... ]
        list_items = list()
        for elem in use2var:
            try:
               title = str(SCDoc.objects.get(pk=elem[1]))
            except SCDoc.DoesNotExist:
                title = ''
            list_items.append({'name': simple_cache.get(elem[0]), 
                               'numbers': str(elem[2])[1:-1], 
                               'title': title})
        
        html = render_to_string('index/add_over_ajax.html', context={'list_items': list_items})
        tmp_dict['html'] = html
        tmp_dict['mes']  = tmpl_message
    else:
        #form.errors
        pass
    #return HttpResponse(html)
    return JsonResponse(tmp_dict, safe=False)


@check_ajax_auth
def transfer_to_stock(request):
    """Возврат исчерпаного картриджа от пользователя обратно на склад.
    """
    if request.method != 'POST':
        return HttpResponse('<h1>' + _('Only use POST requests!') + '</h1>')    

    checked_cartr = request.POST.getlist('selected[]')
    list_cplx = [] 
    ansver = dict()
    for inx in checked_cartr:
        m1 = CartridgeItem.objects.get(pk=inx)
        m1.cart_status = 3     # пустой объект на складе
        tmp_dept = m1.departament
        m1.departament = request.user.departament
        m1.cart_date_change = timezone.now()
        m1.save()
        list_cplx.append((m1.id, str(m1.cart_itm_name), str(tmp_dept), m1.cart_number))

    sign_tr_empty_cart_to_stock.send(sender=None, list_cplx=list_cplx, request=request)
    ansver['error'] = '0'
    ansver['text']   = _('Cartridges successfully moved.')
    return JsonResponse(ansver, safe=False)


@check_ajax_auth
def clear_session(request):
    """Очищаем сессионную переменную от cumulative_list
    """
    request.session['cumulative_list'] = None
    return HttpResponse(_('Session cleared'))


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


@check_ajax_auth
@is_admin
def del_node(request):
    """Удаляем нод(у)(ы) из структуры организации
    """
    ar = request.POST.getlist('selected[]')
    ar = [int(i) for i in ar ]
    le = int(request.POST.get('len', ''))
    for ind in ar:
        node = OrganizationUnits.objects.get(pk=ind)
        node.delete()
    return HttpResponse(_('Data deleted!'))


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

    return HttpResponse(_('Cartridjes deleted!'))
