# -*- coding:utf-8 -*-

import json
from django.db import transaction
from django.db import models
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from common.helpers import is_admin
from events.models import Events
from events.helpers import events_decoder
from index.models import ( City, 
                           CartridgeItem, 
                           OrganizationUnits, 
                           CartridgeItemName, 
                           FirmTonerRefill )
from index.helpers import check_ajax_auth, LastNumber
from index.signals import ( sign_turf_cart, 
                            sign_add_full_to_stock, 
                            sign_tr_empty_cart_to_stock,
                            sign_tr_cart_to_basket, 
                            sign_add_empty_to_stock, 
                            sign_tr_cart_to_uses, 
                            sign_tr_empty_cart_to_firm, ) 
from index.forms.add_items import AddItems
from index.forms.tr_to_firm import TransfeToFirm
from docs.models import SCDoc, RefillingCart
from common.helpers import is_admin

import logging
logger = logging.getLogger(__name__)

@check_ajax_auth
@is_admin
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
        cart_type    = request.POST.get('cart_type')
        if data_in_post.get('doc'):
            cart_doc_id = data_in_post.get('doc')
        else:
            cart_doc_id = 0
        cart_count   = int(data_in_post.get('cartCount'))
        try:
            root_ou   = request.user.departament
            children  = root_ou.get_family()
        except AttributeError:
            children = ''

        # чтобы не плодить лишние сущности зделано одно вью для добавления разных картриджей
        if cart_type == 'full':
            cart_status = 1
        elif cart_type == 'empty':
            cart_status = 3
        else:
            tmp_dict['error'] ='1'
            tmp_dict['mes']   = _('Error in attrib "data" in input button add_item')
            return JsonResponse(tmp_dict)

        # находим нужный номер для отсчёта добавления новых картриджей
        num_obj      = LastNumber(request)
        cart_number  = num_obj.get_num()
        list_cplx    = []
        # Добавляем картриджи в БД
        with transaction.atomic():
            for i in range(cart_count):
                m1 = CartridgeItem(cart_number=cart_number,
                                   cart_itm_name=data_in_post.get('cartName'),
                                   cart_date_added=timezone.now(),
                                   cart_date_change=timezone.now(),
                                   cart_number_refills=0,
                                   departament=request.user.departament,
                                   cart_status=cart_status,
                                   delivery_doc=cart_doc_id,
                                   )
                m1.save()
                list_cplx.append((m1.id, cart_number, cart_name))
                cart_number += 1
            num_obj.last_number = cart_number
            num_obj.commit()
        
        if cart_count == 1:
            tmpl_message = _('Cartridge successfully added.')
        elif cart_count > 1:
            tmpl_message = _('Cartridges successfully added.')

        # запускаем сигнал добавления событий
        if cart_status == 1:
            sign_add_full_to_stock.send(sender=None, list_cplx=list_cplx, request=request)
        elif cart_status == 3:
            sign_add_empty_to_stock.send(sender=None, list_cplx=list_cplx, request=request)
        else:
            pass

        # заполняем тупой кэш нужными данными названий картриджей и их айдишников, это минимизирует обращения к базе
        # в будующем
        simple_cache = dict()
        list_names = CartridgeItemName.objects.all()
        for elem in list_names:
            simple_cache[elem.pk] = elem.cart_itm_name

        numbers = [ i[1] for i in list_cplx ]
        # для экономного расходования дискового пространства будем использовать идешники
        tmp_list = [cart_name_id, cart_doc_id, numbers]
        if cart_status == 1:
            # наполняем сессионную переменную cumulative_list если производится 
            # добавление новых картриджей на склад
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
                # если сессионная cumulative_list пуста
                use2var = [ tmp_list ]
                tmp_list = json.dumps(use2var)
                request.session['cumulative_list'] = tmp_list
        elif cart_status == 3:
            # наполняем сессионную переменную empty_cart_list если производится 
            # добавление БУшных картриджей на склад
            if request.session.get('empty_cart_list', False):
                # если в сессионной переменной уже что-то есть
                session_data = request.session.get('empty_cart_list')
                session_data = json.loads(session_data)
                session_data.append(tmp_list)
                use2var = session_data
                session_data = json.dumps(session_data)
                # перезаписываем переменную в сессии новыми значениями
                request.session['empty_cart_list'] = session_data
            else:
                # если сессионная empty_cart_list пуста
                use2var = [ tmp_list ]
                tmp_list = json.dumps(use2var)
                request.session['empty_cart_list'] = tmp_list

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
def transfer_to_firm(request):
    """Передача картриджей на обслуживание.
    """
    ansver = dict()
    if request.method != 'POST':
        return HttpResponse('<h1>' + _('Only use POST requests!') + '</h1>')    

    form = TransfeToFirm(request.POST)
    if form.is_valid():
        data_in_post = form.cleaned_data
        numbers      = data_in_post.get('numbers')
        firm         = data_in_post.get('firm')
        doc_id       = data_in_post.get('doc')
        price        = data_in_post.get('price')
        firm         = FirmTonerRefill.objects.get(pk=firm) 
        # генерируем запись о заправке
        jsoning_list = []
        for inx in numbers:
            cart_number = CartridgeItem.objects.get(pk=inx).cart_number
            cart_name   = CartridgeItem.objects.get(pk=inx).cart_itm_name
            jsoning_list.append([cart_number, str(cart_name)])
        jsoning_list = json.dumps(jsoning_list)
        
        try:
            doc_id = int(doc_id)
        except:
            doc_id = 0

        try:
            doc = SCDoc.objects.get(pk=doc_id)
        except SCDoc.DoesNotExist:
            doc = Null
        # генерируем номер акта передачи на основе даты и его порядкового номера
        sender_acts = RefillingCart.objects.filter(departament=request.user.departament).count()
        if sender_acts:
            act_number   = sender_acts + 1
            act_number   = str(timezone.now().year) + '_' + str(sender_acts)
        else:
            act_number   = str(timezone.now().year) + '_1'

        act_doc = RefillingCart(number       = act_number,
                                date_created = timezone.now(),
                                firm         = firm,
                                user         = str(request.user),
                                json_content = jsoning_list,
                                money        = price,
                                parent_doc   = doc,
                                departament  = request.user.departament
                               )
        act_doc.save()
        list_cplx = list()
        for inx in numbers:
            m1 = CartridgeItem.objects.get(pk=inx)
            m1.cart_status = 4 # находится на заправке
            m1.filled_firm = firm
            m1.cart_date_change = timezone.now()
            m1.save()
            list_cplx.append((m1.pk, str(m1.cart_itm_name), m1.cart_number))
            
        sign_tr_empty_cart_to_firm.send(sender=None, 
                                        list_cplx=list_cplx, 
                                        request=request, 
                                        firm=str(firm)
                                        )
        ansver['success'] = _('Cartridges %(cart_nums)s successfully moved to firm.') % {'cart_nums': str(numbers)}
    else:
        # если форма содержит ошибки, то сообщаем о них пользователю.
        error_messages = dict([(key, [error for error in value]) for key, value in form.errors.items()])
        ansver['errors'] = error_messages
        print('error_messages = ', error_messages)
    return JsonResponse(ansver)


@check_ajax_auth
def clear_session(request):
    """Очищаем сессионные переменные
    """
    cart_type    = request.POST.get('cart_type')
    if cart_type == 'full':
        request.session['cumulative_list'] = None
    elif cart_type == 'empty':
        request.session['empty_cart_list'] = None
    else:
        pass
    
    return HttpResponse(_('Session cleared'))


@check_ajax_auth
def city_list(request):
    """Возвращает список городов полученных из базы в ввиде json.
    """
    cites = City.objects.all()
    tmp_dict = {}
    for elem in cites:
        tmp_dict[elem.id] = elem.city_name

    return JsonResponse(tmp_dict, safe=False)


@check_ajax_auth
@is_admin
def del_node(request):
    """Удаляем нод(у)(ы) из структуры организации
    """
    ansver = dict()
    ar = request.POST.getlist('selected[]')
    ar = [int(i) for i in ar ]
    if settings.DEMO:
        ansver['error'] = '1'
        ansver['text']  = _('In demo remove nodes not allow.')
        return JsonResponse(ansver)
    try:
        for ind in ar:
            node = OrganizationUnits.objects.get(pk=ind)
            node.delete()
    except models.ProtectedError:
        ansver['error'] = '1'
        ansver['text']  = _('But it can not be removed because other objects reference it.<br/>Error code: 102')
    else:
        ansver['error'] = '0'
        if len(ar) == 1:
            ansver['text']  = _('Name deleted successfully.')
        else:
            ansver['text']  = _('Names deleted successfully.')
    return JsonResponse(ansver)


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


@check_ajax_auth
def transfer_to_basket(request):
    """Перемещение картриджей в корзину.
    """
    if request.method != 'POST':
        return HttpResponse('<h1>' + _('Only use POST requests!') + '</h1>')
    
    ansver = dict()
    checked_cartr = request.POST.getlist('selected[]')
    action_type   = request.POST.get('atype', '')
    try:
        checked_cartr = [int(i) for i in checked_cartr ]
    except ValueError:
        ansver['error'] = '1'
        ansver['text']   = _('Error converting string numbers to int.')
        return JsonResponse(ansver)
    
    if action_type == '5':
        # перемещаем заправленный картридж в корзину
        cart_status = 5
    elif action_type == '6':
        # перемещаем пустой картридж в корзину
        cart_status = 6
    else:
        ansver['error'] = '1'
        ansver['text']   = _('This action type not implemented.')
        return JsonResponse(ansver)

    list_cplx = []
    for inx in checked_cartr:
        m1 = CartridgeItem.objects.get(pk=inx)
        m1.cart_status = cart_status  # в корзинку картриджи  
        m1.departament = request.user.departament
        m1.cart_date_change = timezone.now()
        m1.save()
        list_cplx.append((m1.id, str(m1.cart_itm_name), m1.cart_number))
    
    sign_tr_cart_to_basket.send(sender=None, list_cplx=list_cplx, request=request)
    ansver['error'] = '0'
    ansver['text']   = _('Cartridges successfully transferred to basket.')
    return JsonResponse(ansver)


@check_ajax_auth
def names_suggests(request):
    """
    """
    if request.method != 'POST':
        return HttpResponse('<h1>' + _('Only use POST requests!') + '</h1>')

    ansver   = dict()
    tmp_list = list()
    cart_name       = request.POST.get('cart_name', '')
    cart_name       = cart_name.strip()
    if cart_name:
        names_list      = CartridgeItemName.objects.filter(cart_itm_name__icontains=cart_name)
        for name_item in names_list:
            tmp_list.append([name_item.pk, name_item.cart_itm_name])
        ansver['res']  = tmp_list
    else:
        ansver['res']   = [['', '']]
    return JsonResponse(ansver)


@check_ajax_auth
def get_cart_ou(request):
    """Получение списка установленных РМ у пользователя
    """
    if request.method != 'POST':
        return HttpResponse('<h1>' + _('Only use POST requests!') + '</h1>')

    ansver  = dict()
    context = dict()
    id_ou = request.POST.get('id_ou', '')
    departament = OrganizationUnits.objects.get(pk=id_ou)
    context['list_items'] = CartridgeItem.objects.filter(departament=departament)
    ansver['html'] = render_to_string('index/get_cart_ou.html', context)
    return JsonResponse(ansver)

@check_ajax_auth
def move_to_use(request):
    """
    """
    if request.method != 'POST':
        return HttpResponse('<h1>' + _('Only use POST requests!') + '</h1>')

    ansver  = dict()
    data_in_post = request.POST
    moved = request.POST.getlist('moved[]')
    id_ou = data_in_post['id_ou']
    installed = request.POST.getlist('installed[]')
    # производим фильтрацию полученных данных
    try:
        installed = [int(i) for i in installed]
        moved     = [int(i) for i in moved]
        id_ou     = int(id_ou) 
    except ValueError as e:
        ansver['error'] = '1'
        ansver['text'] = str(e)
        return JsonResponse(ansver)
    
    get = lambda node_id: OrganizationUnits.objects.get(pk=node_id)
    list_cplx = []
    for inx in moved:
        m1 = CartridgeItem.objects.get(pk=inx)
        m1.cart_status = 2 # объект находится в пользовании
        m1.departament = get(id_ou)
        m1.cart_date_change = timezone.now()
        m1.save()
        
        list_cplx.append((m1.id, str(m1.cart_itm_name), m1.cart_number))
    sign_tr_cart_to_uses.send(sender=None, 
                                        list_cplx=list_cplx,
                                        request=request,
                                        org=str(get(id_ou)))

    list_cplx = [] 
    if  installed:
        for inx in installed:
            m1 = CartridgeItem.objects.get(pk=inx)
            m1.cart_status = 3     # пустой объект на складе
            tmp_dept = m1.departament
            m1.departament = request.user.departament
            m1.cart_date_change = timezone.now()
            m1.save()
            list_cplx.append((m1.id, str(m1.cart_itm_name), str(tmp_dept), m1.cart_number))

        sign_tr_empty_cart_to_stock.send(sender=None, list_cplx=list_cplx, request=request)
   
    ansver['error'] = '0'
    ansver['url']   = reverse('stock')
    
    return JsonResponse(ansver)

@check_ajax_auth
def view_events(request):
    """Загрузка блока с событиями для страницы dashboard
    """
    ansver  = dict()
    context = dict()
    time_zone_offset = request.POST.get('time_zone_offset', 0);
    detail           = request.POST.get('detail', 0) 
    try:
        time_zone_offset = int(time_zone_offset)
    except ValueError:
        time_zone_offset = 0

    try:
        dept_id = request.user.departament.pk
    except AttributeError:
        dept_id = 0
    
    try:
        detail = int(detail)
    except ValueError:
        detail = 0

    MAX_EVENT_LIST = settings.DASHBOARD_EVENT_LIST
    if detail:
        events_list = Events.objects.filter(departament=dept_id).order_by('-pk')[:MAX_EVENT_LIST]
        context['count_events'] = len(events_list)
        if events_list.count() >= MAX_EVENT_LIST:
            context['show_more'] = True
        else:
            context['show_more'] = False
        context['events_list'] = events_decoder(events_list, time_zone_offset, simple=False)
        html = render_to_string('events/show_all_events.html', context)
    else:
        events_list = Events.objects.filter(departament=dept_id).order_by('-pk')[:MAX_EVENT_LIST]
        if events_list.count() >= MAX_EVENT_LIST:
            context['show_more'] = True
        else:
            context['show_more'] = False
        context['events_list'] = events_decoder(events_list, time_zone_offset, simple=False)
        html = render_to_string('index/events.html', context)
    
    ansver['html'] = html
    return JsonResponse(ansver)
