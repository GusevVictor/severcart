# -*- coding:utf-8 -*-

import json, pytz
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db import models
from django.utils import timezone
from django.http import JsonResponse, Http404, HttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.db.models import Q
from common.helpers import is_admin
from django.views.decorators.http import require_POST
from events.models import Events
from index.forms.tr_to_firm import TransfeToFirmScanner
from events.helpers import events_decoder, do_timezone
from index.models import ( City, 
                           CartridgeItem, 
                           OrganizationUnits, 
                           CartridgeItemName, 
                           FirmTonerRefill,
                           STATUS )
from index.helpers import check_ajax_auth, LastNumber, str2int
from index.signals import ( sign_turf_cart, 
                            sign_add_full_to_stock, 
                            sign_tr_empty_cart_to_stock,
                            sign_tr_cart_to_basket, 
                            sign_add_empty_to_stock, 
                            sign_tr_cart_to_uses, 
                            sign_tr_empty_cart_to_firm,
                            sign_change_number, 
                            )
from index.forms.add_items import AddItems
from index.forms.add_items_from_barcode import AddItemsFromBarCodeScanner
from index.forms.tr_to_firm import TransfeToFirm
from docs.models import SCDoc, RefillingCart
from service.helpers import SevercartConfigs

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
        cart_in_firm = CartridgeItem.objects.filter(filled_firm=firm).count()
        if cart_in_firm == 0:
            firm.delete()
            resp_dict['text']  = _('Firm deleted!')
            resp_dict['error'] = '0'
        else:
            resp_dict['text']  = _('You can not delete, because have cartridges at a gas station.')
            resp_dict['error'] = '1'
    return JsonResponse(resp_dict)


def search_number(cart_number, request):
    """Хелпер функция для поиска дублей номеров внутри представительства.
       Обработчиком запроса не является.
    """
    cart_items = CartridgeItem.objects.filter(cart_number=cart_number)
    try:
        root_ou   = request.user.departament
        des       = root_ou.get_descendants(include_self=True)
    except:
        cart_items = []
    else:
        cart_items = cart_items.filter(departament__in=des)
    return cart_items


@require_POST
@check_ajax_auth
def ajax_add_session_items(request):
    """Довляем новые картриджи на склад через Аякс
    """
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
        storages     = data_in_post.get('storages')
        storages     = storages.pk
        cart_name    = str(cart_name)
        cart_type    = request.POST.get('cart_type')
        cart_doc_id  = data_in_post.get('doc')
        cart_count   = int(data_in_post.get('cartCount'))
        # фича добавленна после обращения пользователя из Новосибирска
        tumbler = request.POST.get('tumbler', 0) # отвечает за ручной ввод номера РМ
        tumbler_2 = request.POST.get('tumbler_2', 0) # отвечает за ручноую установку даты добавления РМ на склад
        tumbler = str2int(tumbler)
        tumbler_2 = str2int(tumbler_2)
        if tumbler_2:
            conf = SevercartConfigs()
            date_added = data_in_post.get('set_date')
            time_added = data_in_post.get('time')
            set_date = datetime(year=date_added['year'], 
                                month=date_added['month'], 
                                day=date_added['day'], 
                                hour=time_added['hours'], 
                                minute=time_added['minutes'], 
                                second=0, microsecond=0 )
                                #, tzinfo=pytz.timezone(conf.time_zone))
            # d = datetime.datetime.now()
            local = pytz.timezone(conf.time_zone)
            local_dt = local.localize(set_date, is_dst=None)
            date_time_added = local_dt.astimezone(pytz.utc)
        else:
            date_time_added = timezone.now()
        # чтобы не плодить лишние сущности зделано одно вью для добавления разных картриджей
        if cart_type == 'full':
            cart_status = 1
        elif cart_type == 'empty':
            cart_status = 3
        else:
            tmp_dict['error'] ='1'
            tmp_dict['mes']   = _('Error in attrib "data" in input button add_item')
            return JsonResponse(tmp_dict)

        list_cplx    = list()
        if tumbler:
            # если переключатель ручного ввода номера включен
            cart_number = request.POST.get('cart_number')
            cart_number = cart_number.strip()
            # далее выполняем проверку на дубли, только внутри своего представительства
            cart_items = search_number(cart_number, request)

            if len(cart_items):
                tmp_dict['error'] = '1'
                tmp_dict['mes'] = _('An object with this number has already been registered.')
                return JsonResponse(tmp_dict)
        else:    
            # если тумблер ручного ввода номера РМ НЕ установлен, то генерируем новый свободный номер
            # находим нужный номер для отсчёта добавления новых картриджей
            num_obj      = LastNumber(request)
            cart_number  = num_obj.get_num()

            # перед тем как выполняется сохранение, производим поиск дубля
            # выполняем генерацию новых номеров пока не найдём свободный
            while len(search_number(cart_number, request)):
                cart_number += 1

        # Добавляем картриджи в БД
        with transaction.atomic():
            for i in range(cart_count):
                m1 = CartridgeItem(sklad=storages,
                                   cart_number=str(cart_number),
                                   cart_itm_name=data_in_post.get('cartName'),
                                   cart_date_added=date_time_added,
                                   cart_date_change=date_time_added,
                                   cart_number_refills=0,
                                   departament=request.user.departament,
                                   cart_status=cart_status,
                                   delivery_doc=cart_doc_id,
                                   )
                m1.save()
                list_cplx.append((m1.id, str(cart_number), cart_name))
                if not(tumbler):
                    try:
                        # перестрахуемся
                        cart_number = int(cart_number)
                    except ValueError:
                        cart_number = 0    
                    cart_number += 1
                    # перед тем как выполняется сохранение, производим поиск дубля
                    # выполняем генерацию новых номеров пока не найдём свободный
                    while len(search_number(cart_number, request)):
                        cart_number += 1

                    num_obj.last_number = str(cart_number)
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
                               'numbers': str(elem[2])[1:-1].replace('\'',''), 
                               'title': title})
        
        html = render_to_string('index/add_over_ajax.html', context={'list_items': list_items})
        tmp_dict['html'] = html
        tmp_dict['mes']  = tmpl_message
    else:
        #form.errors
        pass
    return JsonResponse(tmp_dict, safe=False)


@require_POST
@check_ajax_auth
def ajax_add_session_items_from_barcode(request):
    """Добавляем картриджи в сессионную переменную с помощью сканера штрих кодов.
    """
    # если пришёл запрос то пополняем сессионную переменную
    # результаты отображаем на странице
    context = dict()
    try:
        m1 = request.user.departament.pk
    except AttributeError:
        context['mes']  = _('User not assosiate with organization unit!<br/>Error code: 101.')
        context['error'] = '1'
        return JsonResponse(context)
    
    context['error'] = '0'
    form = AddItemsFromBarCodeScanner(request.POST)
    if not(form.is_valid()):
        # если в БД уже есть РМ дубль с аналогичным номером, то
        # прекращаем выполнение программы и сообщаем об ошибке
        context['mes'] = form.errors.as_text()
        context['error'] = '1'
        return JsonResponse(context)

    if form.is_valid():
        data_in_post = form.cleaned_data
        cart_number  = data_in_post.get('cartNumber')
        cart_name    = data_in_post.get('cartName').cart_itm_name
        storages     = data_in_post.get('storages')
        storages     = storages.pk
        cart_name    = str(cart_name)
        cart_name_id = data_in_post.get('cartName').pk
        cart_type    = request.POST.get('cart_type')
        cart_doc_id  = data_in_post.get('doc')

        tumbler      = data_in_post.get('tumbler')
        # чтобы не плодить лишние сущности зделано одно вью для добавления разных картриджей
        if cart_type == 'full':
            #cart_status = 1
            session_var = 'add_cartridges_full_in_stock'
        elif cart_type == 'empty':
            #cart_status = 3
            session_var = 'add_cartridges_empty_in_stock'
        else:
            context['error'] ='1'
            context['mes']   = _('Error in attrib "data" in input button add_item')
            return JsonResponse(context)

        conf = SevercartConfigs()
        # проверяем на дубли имеющихся номеров
        cart_items = search_number(cart_number, request)
        if len(cart_items):
            context['error'] = '1'
            context['mes'] = _('An object with this number has already been registered.')
            return JsonResponse(context)

        if tumbler:
            date_added = data_in_post.get('set_date')
            time_added = data_in_post.get('time')
            set_date = datetime(year=date_added['year'], 
                                month=date_added['month'], 
                                day=date_added['day'], 
                                hour=time_added['hours'], 
                                minute=time_added['minutes'], 
                                second=0, microsecond=0 )
                                #, tzinfo=pytz.timezone(conf.time_zone))
            # d = datetime.datetime.now()
            local = pytz.timezone(conf.time_zone)
            local_dt = local.localize(set_date, is_dst=None)
            date_time_added = local_dt.astimezone(pytz.utc)
            date_time_added_show = set_date
        else:
            date_time_added = timezone.now()
            date_time_added_show = do_timezone(date_time_added, conf.time_zone)

        # собираем очект РМ на основе полученных данных
        cart_obj = dict()
        cart_obj['cart_number'] = cart_number
        cart_obj['cart_name'] = cart_name
        cart_obj['cart_name_id'] = cart_name_id
        cart_obj['storages'] = storages
        cart_obj['cart_doc_id'] = cart_doc_id
        cart_obj['cart_type'] = cart_type
        #local = pytz.timezone(conf.time_zone)
        #date_time_added = local.localize(date_time_added, is_dst=None)
        cart_obj['date_time_added'] = date_time_added
        cart_obj['date_time_added_show'] = date_time_added_show
        # Добавляем отсканированный картридж в БД
        if request.session.get(session_var, False):
            # если в сессионной переменной уже что-то есть
            session_data = request.session.get(session_var)
            # проверяем добавляем элемент на дубль в сессионной казине
            exist = False
            for elem in session_data:
                
                if elem['cart_number'] in cart_number:
                    exist = True
                    break
            if exist:
                message = _('Cartridge %(cart_number)s  is already in the basket session.') % {'cart_number': cart_number}                
                context['mes']  = message
                context['error'] = '1'
                return JsonResponse(context)

            #session_data.append(cart_obj)
            session_data.insert(0, cart_obj)
        else:
            # если сессионная basket_to_transfer_firm пуста или её нет вообще
            session_data = list()
            #session_data.append(cart_obj)
            session_data.insert(0, cart_obj)
        request.session[session_var] = session_data

        message = _('Cartridge %(cart_number)s successfully added in session basket.') % {'cart_number': cart_number}
        html = render_to_string('index/add_items_barcode_ajax.html', context={'list_items': session_data})
        context['html'] = html
        context['mes']  = message
        context['error'] = '0'
    return JsonResponse(context)


@require_POST
@check_ajax_auth
def add_items_in_stock_from_session_basket(request):
    """Добавление объектов на склад, в соответствии с содержанием сессионных переменных.
       Требуется доробтка.
    """
    ansver = dict()
    session_var = request.POST.get('session_var', '')
    session_var = session_var.strip()
    if session_var == 'add_cartridges_full_in_stock':
        cart_status = 1
    elif session_var == 'add_cartridges_empty_in_stock':
        cart_status = 3
    else:
        ansver['error'] = '1'
        ansver['text'] = _('Session varible not emplimented.')
        return JsonResponse(ansver)

    if request.session.get(session_var, False):
        session_data = request.session.get(session_var)
    else:
        ansver['error'] = '1'
        ansver['text'] = _('Cart is empty. Add nothing to the warehouse.')
        return JsonResponse(ansver)

    list_cplx = list()
    number_list = list()
    with transaction.atomic():
        for cartridge in session_data:
            
            cart_name = CartridgeItemName.objects.get(pk=cartridge['cart_name_id'])

            m1 = CartridgeItem(sklad=str2int(cartridge['storages']),
                               cart_number=cartridge['cart_number'],
                               cart_itm_name=cart_name,
                               cart_date_added=cartridge['date_time_added'],
                               cart_date_change=cartridge['date_time_added'],
                               cart_number_refills=0,
                               departament=request.user.departament,
                               cart_status=cart_status,
                               delivery_doc=cartridge['cart_doc_id'],
                               )
            m1.save()
            number_list.append(cartridge['cart_number'])
            list_cplx.append((m1.id, cartridge['cart_number'], cart_name))
    ansver['text'] = _('Cartridges %(cart_numbers)s successfully added.') % {'cart_numbers': number_list}
    ansver['error'] = '0'

    # очищаем сессионную переменную
    request.session[session_var] = None

    # запускаем сигнал добавления событий
    if cart_status == 1:
        sign_add_full_to_stock.send(sender=None, list_cplx=list_cplx, request=request)
    elif cart_status == 3:
        sign_add_empty_to_stock.send(sender=None, list_cplx=list_cplx, request=request)
    else:
        pass

    return JsonResponse(ansver)


@require_POST
@check_ajax_auth
def transfer_to_stock(request):
    """Возврат исчерпаного картриджа от пользователя обратно на склад.
    """
    checked_cartr = request.POST.getlist('selected[]')
    list_cplx = [] 
    ansver = dict()
    with transaction.atomic():
        for inx in checked_cartr:
            m1 = CartridgeItem.objects.get(pk=inx)
            # проверяем принадлежность перемещаемого РМ департаменту 
            # пользователя.
            if m1.departament in request.user.departament.get_descendants():
                m1.cart_status = 3     # пустой объект на складе
                tmp_dept = m1.departament
                m1.departament = request.user.departament
                m1.cart_date_change = timezone.now()
                m1.save()
                list_cplx.append((m1.id, str(m1.cart_itm_name), str(tmp_dept), m1.cart_number))

    if list_cplx:
        sign_tr_empty_cart_to_stock.send(sender=None, list_cplx=list_cplx, request=request)
    ansver['error'] = '0'
    ansver['text']   = _('Cartridges successfully moved.')
    return JsonResponse(ansver, safe=False)


@require_POST
@check_ajax_auth
def transfer_to_firm(request):
    """Передача картриджей на обслуживание.
    """
    ansver = dict()
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
            doc = None
        # генерируем номер акта передачи на основе даты и его порядкового номера
        sender_acts = RefillingCart.objects.filter(departament=request.user.departament).count()
        if sender_acts:
            act_number   = sender_acts + 1
            act_number   = str(timezone.now().year) + '_' + str(sender_acts)
        else:
            act_number   = str(timezone.now().year) + '_1'

        # сохраняем в БД акт передачи РМ на заправку
        act_doc = RefillingCart(
                                doc_type     = 1,        # документ передачи на запраку
                                number       = act_number,
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
        show_numbers = list()
        for inx in numbers:
            m1 = CartridgeItem.objects.get(pk=inx)
            # проверяем принадлежность перемещаемого РМ департаменту 
            # пользователя.
            if m1.departament == request.user.departament:
                m1.cart_status = 4 # находится на заправке
                m1.filled_firm = firm
                m1.cart_date_change = timezone.now()
                m1.save()
                list_cplx.append((m1.pk, str(m1.cart_itm_name), m1.cart_number))
                show_numbers.append(m1.cart_number)
        
        if list_cplx:
            sign_tr_empty_cart_to_firm.send(sender=None, 
                                            list_cplx=list_cplx, 
                                            request=request, 
                                            firm=str(firm) + ':' + str(firm.pk) # сохраняем в логах событий имя и Id фирмы контрагента.
                                            )
        show_numbers = str(show_numbers)
        # Убираем лишние авпострофы из списка с номерами
        show_numbers = show_numbers.replace('\'', '')
        if len(show_numbers):
            msg = _('Cartridges %(cart_nums)s successfully moved to firm.') % {'cart_nums': show_numbers}
        else:
            msg = _('No transmission facilities')
        
        ansver['success'] = '1'
        ansver['url']   = reverse('index:empty')
        messages.success(request, msg)
    else:
        # если форма содержит ошибки, то сообщаем о них пользователю.
        error_messages = dict([(key, [error for error in value]) for key, value in form.errors.items()])
        ansver['errors'] = error_messages
    return JsonResponse(ansver)


@require_POST
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


@require_POST
@check_ajax_auth
def city_list(request):
    """Возвращает список городов полученных из базы в ввиде json.
    """
    cites = City.objects.all()
    tmp_dict = {}
    for elem in cites:
        tmp_dict[elem.id] = elem.city_name

    return JsonResponse(tmp_dict, safe=False)


@require_POST
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
        # проверяем принадлежность перемещаемого РМ департаменту 
        # пользователя.
        if node.departament == request.user.departament:
            list_cplx.append((node.id, str(node.cart_itm_name), node.cart_number))
            node.delete()
    
    if list_cplx:
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
        # проверяем принадлежность перемещаемого РМ департаменту 
        # пользователя.
        if (m1.departament in request.user.departament.get_descendants()) or \
           (m1.departament == request.user.departament):
            m1.cart_status = cart_status
            m1.departament = request.user.departament
            m1.cart_date_change = timezone.now()
            m1.save()
            list_cplx.append((m1.id, str(m1.cart_itm_name), m1.cart_number))
    
        if list_cplx:
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
    """Передача РМ в пользование.
    """
    if request.method != 'POST':
        return HttpResponse('<h1>' + _('Only use POST requests!') + '</h1>')

    ansver  = dict()
    data_in_post = request.POST
    moved = request.POST.getlist('moved[]')
    id_ou = data_in_post['id_ou']
    installed = request.POST.getlist('installed[]')
    try:
        installed = [int(i) for i in installed]
        moved     = [int(i) for i in moved]
        id_ou     = int(id_ou) 
    except ValueError as e:
        ansver['error'] = '1'
        ansver['text'] = str(e)
        return JsonResponse(ansver)
    
    get = lambda node_id: OrganizationUnits.objects.get(pk=node_id)
    list_cplx = list()
    show_numbers = list() # используется для информационных сообщений
    try:
        root_ou   = request.user.departament
        des       = root_ou.get_descendants()
    except:
        pass
    with transaction.atomic():
        for inx in moved:
            m1 = CartridgeItem.objects.get(pk=inx)
            # проверяем принадлежность перемещаемого РМ департаменту 
            # пользователя.
            if m1.departament == request.user.departament:
                m1.cart_status = 2 # объект находится в пользовании
                m1.departament = get(id_ou)
                m1.cart_date_change = timezone.now()
                show_numbers.append(m1.cart_number)
                m1.save()
                list_cplx.append((m1.id, str(m1.cart_itm_name), m1.cart_number))
        
    if list_cplx:
        sign_tr_cart_to_uses.send(sender=None, list_cplx=list_cplx, request=request, org=str(get(id_ou)))

    list_cplx = []
    if  installed:
        # если выбрано возврат РМ от пользователя обратно на склад
        with transaction.atomic():
            for inx in installed:
                # проверяем принадлежность перемещаемого РМ департаменту 
                # пользователя.
                m1 = CartridgeItem.objects.get(pk=inx)
                if m1.departament in des:
                    m1.cart_status = 3     # пустой объект на складе
                    tmp_dept = m1.departament
                    m1.departament = request.user.departament
                    m1.cart_date_change = timezone.now()
                    m1.save()
                    list_cplx.append((m1.id, str(m1.cart_itm_name), str(tmp_dept), m1.cart_number))

        if list_cplx:
            sign_tr_empty_cart_to_stock.send(sender=None, list_cplx=list_cplx, request=request)
   
    ansver['error'] = '0'
    ansver['url']   = reverse('index:stock')
    show_numbers = str(show_numbers)
    show_numbers = show_numbers.replace('\'', '')
    msg = _('Cartridges %(cart_list)s successfully transferred for use') % {'cart_list': show_numbers}
    messages.success(request, msg)
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

@check_ajax_auth
def from_basket_to_stock(request):
    """Возврат обратно картриджей на склад из корзины
    """
    ansver  = dict()
    ar = request.POST.getlist('selected[]')
    try:
        ar = [int(i) for i in ar ]
    except:
        # если пользователь сфальсифицировал запрос то
        # ничего не делаем и возвращаем пустой ответ
        raise Http404

    for inx in ar:
        m1 = CartridgeItem.objects.get(pk=inx)
        # проверяем принадлежность перемещаемого РМ департаменту 
        # пользователя.
        if m1.departament == request.user.departament:
            if m1.cart_status == 5:
                m1.cart_status = 1  # возвращаем обратно на склад заполненным
            elif m1.cart_status == 6:
                m1.cart_status = 3  # возвращаем обратно на склад пустым    
            else:
                raise Http404
            m1.cart_date_change = timezone.now()
            m1.save()
    return JsonResponse(ansver)


@check_ajax_auth
@is_admin
def change_ou_name(request):
    """Изменение имени организационного подразделения.
    """
    if request.method != 'POST':
        return HttpResponse('<h1>' + _('Only use POST requests!') + '</h1>')

    ansver = dict()
    ansver['error'] = 1
    ouid = request.POST.getlist('ouid', [])
    ou_name = request.POST.getlist('ou_name', [])
    try:
        ouid = ouid[0]
        ou_name = ou_name[0]
    except:
        raise Http404
    try:
        ouid = int(ouid)
    except ValueError:
        ouid = 0
    try:
        ou = OrganizationUnits.objects.get(pk=ouid)
    except:
        raise Http404
        
    ou.name = ou_name
    ou.save()
    ansver['error'] = 0
    return JsonResponse(ansver)


@require_POST
@check_ajax_auth
def add_object_to_basket_for_firm(request):
    """Подготавливаем списки РМ, передаваемых контрагентам на обслуживание.
    """
    ansver = dict()
    cart_barcode = request.POST.get('barcode', '')
    cart_barcode = cart_barcode.strip()
    try:
        root_ou   = request.user.departament
        des       = root_ou.get_descendants()
    except:
        ansver['error'] ='1'
        ansver['mes']   = _('Error: 101. Not set organization utint.')
        return JsonResponse(ansver)
    else:
        # выполняем поиск РМ обладающие разными статусами
        # например, пуст и на складе, задействованн, ...
        m1 = CartridgeItem.objects.filter(
                                            Q(cart_number=cart_barcode) & 
                                            (Q(departament__in=des)
                                            | Q(departament=root_ou))
                                         )

    if len(m1) >= 1:
        cartridge = m1[0]
        m1 = None
    else:
        # если картридж с данным неомером не найденн
        ansver['error'] ='1'
        ansver['mes']   = _('Consumables with the number %(cart_barcode)s was not found.') % {'cart_barcode' : cart_barcode}
        return JsonResponse(ansver)

    session_data = request.session.get('basket_to_transfer_firm', False)
    if session_data and (str(cartridge.pk) in session_data):
        ansver['error'] ='1'
        ansver['mes']   = _('The object is already in the lists on the move.')
        return JsonResponse(ansver)

    if cartridge.cart_status == 3:
        # если картридж с нужным номером найденн и у него код статуса "Пустой и на складе"
        # добавляем информауию в сессионную переменную пользователя
        if request.session.get('basket_to_transfer_firm', False):
            # если в сессионной переменной уже что-то есть
            session_data = request.session.get('basket_to_transfer_firm')
            # если в сессионной переменной данные уже есть то РМ в список не добавляем
            try:
                session_data.index(cartridge.pk)
            except ValueError: 
                session_data.append(cartridge.pk)
                request.session['basket_to_transfer_firm'] = session_data
            else:
                ansver['error'] ='1'
                ansver['mes'] = _('The object number %(cart_barcode)s is already present in the lists on the move.') % {'cart_barcode': cart_barcode}
                return JsonResponse(ansver)                
        else:
            # если сессионная basket_to_transfer_firm пуста или её нет вообще
            session_data = [ cartridge.pk ]
            request.session['basket_to_transfer_firm'] = session_data
        ansver['error'] ='0'
        ansver['mes'] = _('Consumable material is successfully prepared for transfer')
        ansver['cart_name'] = str(cartridge.cart_itm_name)
        ansver['cart_num'] = str(cartridge.cart_number)
        ansver['pk'] = str(cartridge.pk)
        ansver['moved_list'] = str(session_data)[1:-1]
        return JsonResponse(ansver)
    else:
        cart_status = STATUS[cartridge.cart_status-1][1]
        ansver['error'] ='2'
        ansver['mes'] = _('This consumable is in the state \"%(cart_status)s\". Are you sure you want to place in the lists transmitted?') % {'cart_status': cart_status}
        return JsonResponse(ansver)
    return JsonResponse(ansver)


@require_POST
@check_ajax_auth
def force_move_to_transfer(request):
    """Усиленная попытка перемещения РМ в "списки пустых и на скдале"
    """
    ansver = dict()
    cart_barcode = request.POST.get('barcode', '')
    cart_barcode = cart_barcode.strip()
    try:
        root_ou   = request.user.departament
        des       = root_ou.get_descendants()
    except:
        ansver['error'] ='1'
        ansver['mes']   = _('Error: 101. Not set organization utint.')
        return JsonResponse(ansver)
    
    # выполняем поиск РМ обладающие разными статусами
    # например, пуст и на складе, задействованн, ...
    m1 = CartridgeItem.objects.filter(
                                        Q(cart_number=cart_barcode) & 
                                        (Q(departament__in=des)
                                        | Q(departament=root_ou))
                                     )
    if len(m1) >= 1:
        cartridge = m1[0]
        m1 = None
    else:
        # если картридж с данным неомером не найденн
        ansver['error'] ='1'
        ansver['mes']   = _('Consumables with the number %(cart_barcode)s was not found.') % {'cart_barcode' : cart_barcode}
        return JsonResponse(ansver)

    list_cplx = list()
    # проверяем принадлежность перемещаемого РМ департаменту 
    # пользователя.
    if cartridge.departament in request.user.departament.get_descendants():
        cartridge.cart_status = 3     # пустой объект на складе
        tmp_dept = cartridge.departament
        cartridge.departament = request.user.departament
        cartridge.cart_date_change = timezone.now()
        cartridge.save()
        list_cplx.append((cartridge.id, str(cartridge.cart_itm_name), str(tmp_dept), cartridge.cart_number))

    if list_cplx:
        sign_tr_empty_cart_to_stock.send(sender=None, list_cplx=list_cplx, request=request)

    if request.session.get('basket_to_transfer_firm', False):
        # если в сессионной переменной уже что-то есть
        session_data = request.session.get('basket_to_transfer_firm')
        session_data.append(cartridge.pk)
        request.session['basket_to_transfer_firm'] = session_data
    else:
        # если сессионная basket_to_transfer_firm пуста или её нет вообще
        session_data = [ cartridge.pk, ]
        request.session['basket_to_transfer_firm'] = session_data
    
    ansver['error'] ='0'
    ansver['mes']   = _('Consumable material is successfully prepared for transfer')
    ansver['cart_name'] = str(cartridge.cart_itm_name)
    ansver['cart_num'] = str(cartridge.cart_number)
    ansver['pk'] = str(cartridge.pk)
    return JsonResponse(ansver)


@require_POST
@check_ajax_auth
def remove_session_item(request):
    """Удаление элемента из сессионной переменной перемещения РМ на обслуживание.
    """
    ansver = dict()
    selected = request.POST.getlist('selected[]')
    session_key = request.POST.get('session_key' ,'')
    
    if session_key == 'basket_to_transfer_firm':
        session_key = 'basket_to_transfer_firm'

    elif session_key == 'basket_to_transfer_stock':
        session_key = 'basket_to_transfer_stock'

    else:
        ansver['error'] = '1'
        ansver['mes'] = _('The session key is not recognized.')
        return JsonResponse(ansver)    

    if request.session.get(session_key, []):
        session_data = request.session.get(session_key)
    if session_data:
        for select in selected:
            try:
                select = int(select)
            except ValueError:
                select = 0
            session_data = list(item for item in session_data if select != item)
        request.session[session_key] = session_data
        ansver['error'] = '0'
    ansver['show_remove_session_button'] = True
    if session_data:
        ansver['show_remove_session_button'] = False

    ansver['moved_list'] = str(session_data)[1:-1]
    return JsonResponse(ansver)


@require_POST
@check_ajax_auth
def move_objects_to_firm_with_barcode(request):
    """Аякс обработчик перемещения РМ на обслуживание контрагенту на основе подготовленных
       списков с сканером штрих кодов.
    """
    ansver = dict()
    form = TransfeToFirmScanner(request.POST)
    if form.is_valid():
        data_in_post = form.cleaned_data
        numbers      = data_in_post.get('numbers')
        firm         = data_in_post.get('firm')
        doc          = data_in_post.get('doc')
        try:
            firm = FirmTonerRefill.objects.get(pk=firm) 
        except FirmTonerRefill.DoesNotExist:
            firm = None
        # меняем статусы РМ в БД на основании запросов
        # генерируем запись о заправке
        jsoning_list = []
        for inx in numbers:
            cart_number = CartridgeItem.objects.get(pk=inx).cart_number
            cart_name   = CartridgeItem.objects.get(pk=inx).cart_itm_name
            jsoning_list.append([cart_number, str(cart_name)])
        jsoning_list = json.dumps(jsoning_list)
        
        try:
            doc = int(doc)
        except:
            doc = 0

        try:
            doc = SCDoc.objects.get(pk=doc)
        except SCDoc.DoesNotExist:
            doc = None
        # генерируем номер акта передачи на основе даты и его порядкового номера
        sender_acts = RefillingCart.objects.filter(departament=request.user.departament).count()
        if sender_acts:
            act_number   = sender_acts + 1
            act_number   = str(timezone.now().year) + '_' + str(sender_acts)
        else:
            act_number   = str(timezone.now().year) + '_1'

        # сохраняем в БД акт передачи РМ на заправку
        act_doc = RefillingCart(number       = act_number,
                                date_created = timezone.now(),
                                firm         = firm,
                                user         = str(request.user),
                                json_content = jsoning_list,
                                parent_doc   = doc,
                                departament  = request.user.departament
                               )
        act_doc.save()
        list_cplx = list()
        show_numbers = list()
        with transaction.atomic():
            for inx in numbers:
                m1 = CartridgeItem.objects.get(pk=inx)
                # проверяем принадлежность перемещаемого РМ департаменту 
                # пользователя.
                if m1.departament == request.user.departament:
                    m1.cart_status = 4 # находится на заправке
                    m1.filled_firm = firm
                    m1.cart_date_change = timezone.now()
                    m1.save()
                    list_cplx.append((m1.pk, str(m1.cart_itm_name), m1.cart_number))
                    show_numbers.append(m1.cart_number)
            
        if list_cplx:
            sign_tr_empty_cart_to_firm.send(sender=None, 
                                            list_cplx=list_cplx, 
                                            request=request, 
                                            firm=str(firm)
                                            )
        


        ansver['error'] = '0'
        ansver['url'] = reverse('index:empty')
        msg = _('Objects %(numbers)s moved successfully.') % {'numbers': numbers}
        messages.success(request, msg)
        # очищаем сессионную переменную basket_to_transfer_firm
        request.session['basket_to_transfer_firm'] = []
    else:
        ansver['error'] = '1'
        ansver['text'] = form.errors.as_text
    return JsonResponse(ansver)


def add_object_to_basket_from_firm_to_stock(request):
    """Перемещение объектов в сессию для реализации передачи РМ из обслуживания
       обратно на склад.
    """
    ansver = dict()
    cart_barcode = request.POST.get('barcode', '')
    cart_barcode = cart_barcode.strip()

    try:
        root_ou   = request.user.departament
        des       = root_ou.get_descendants()
    except:
        ansver['error'] ='1'
        ansver['mes']   = _('Error: 101. Not set organization utint.')
        return JsonResponse(ansver)
    else:
        # выполняем поиск РМ обладающие разными статусами
        # например, пуст и на складе, задействованн, ...
        m1 = CartridgeItem.objects.filter(
                                            Q(cart_number=cart_barcode) & 
                                            (Q(departament__in=des)
                                            | Q(departament=root_ou))
                                         )
    if len(m1) >= 1:
        cartridge = m1[0]
        m1 = None
    else:
        # если картридж с данным неомером не найденн
        ansver['error'] ='1'
        ansver['mes']   = _('Consumables with the number %(cart_barcode)s was not found.') % {'cart_barcode' : cart_barcode}
        return JsonResponse(ansver)

    session_data = request.session.get('basket_to_transfer_stock', False)
    if session_data and (str(cartridge.pk) in session_data):
        ansver['error'] ='1'
        ansver['mes']   = _('The object is already in the lists on the move.')
        return JsonResponse(ansver)

    if cartridge.cart_status == 4:
        # если картридж с нужным номером найденн и у него код статуса "На обслуживании"
        # добавляем информауию в сессионную переменную пользователя
        if request.session.get('basket_to_transfer_stock', False):
            # если в сессионной переменной уже что-то есть
            session_data = request.session.get('basket_to_transfer_stock')
            # если в сессионной переменной данные уже есть то РМ в список не добавляем
            try:
                session_data.index(cartridge.pk)
            except ValueError: 
                session_data.append(cartridge.pk)
                request.session['basket_to_transfer_stock'] = session_data
            else:
                ansver['error'] ='1'
                ansver['mes'] = _('The object number %(cart_barcode)s is already present in the lists on the move.') % {'cart_barcode': cart_barcode}
                return JsonResponse(ansver)                
        else:
            # если сессионная basket_to_transfer_stock пуста или её нет вообще
            session_data = [ cartridge.pk ]
            request.session['basket_to_transfer_stock'] = session_data
        ansver['error'] ='0'
        ansver['mes'] = _('Consumable material is successfully prepared for transfer')
        ansver['cart_name'] = str(cartridge.cart_itm_name)
        ansver['cart_num'] = str(cartridge.cart_number)
        ansver['pk'] = str(cartridge.pk)
        ansver['moved_list'] = str(session_data)[1:-1]
        return JsonResponse(ansver)
    else:
        cart_status = STATUS[cartridge.cart_status-1][1]
        ansver['error'] ='2'
        ansver['mes'] = _('This consumable is in the state \"%(cart_status)s\". Return to the warehouse is impossible.') % {'cart_status': cart_status}
        return JsonResponse(ansver)
    return JsonResponse(ansver)


@require_POST
@check_ajax_auth
def rate(request):
    """установка оценки обслуживающей организации, по конкретной единице картриджа.
    """
    ansver = dict()
    action = request.POST.getlist('action')[0]
    firm_id = request.POST.getlist('firm_id')[0]
    cart_id = request.POST.getlist('cart_id')[0]
    firm_id = str2int(firm_id)
    cart_id = str2int(cart_id)

    node = get_object_or_404(CartridgeItem, pk=cart_id)
    firm = get_object_or_404(FirmTonerRefill, pk=firm_id)
    # проверяем принадлежность перемещаемого РМ департаменту 
    # пользователя.
    try:
        root_ou   = request.user.departament
        des       = root_ou.get_descendants()
    except:
        pass

    if not(node.departament in des):
        ansver['error'] = '1'
        ansver['msg'] = _('An object with number %(cart_num)s belong to a different organizational unit.') % {'cart_num': node.cart_number}

    if action == 'set_good':
        rating = firm.vote_plus
        rating += 1
        firm.vote_plus = rating
    elif action == 'set_bad':
        rating = firm.vote_minus
        rating += 1
        firm.vote_minus = rating
    else:
        ansver['error'] = '1'
        ansver['msg'] = _('Action not supported')
        return JsonResponse(ansver)

    firm.save()
    node.vote = True
    node.save()
    ansver['error'] = '0'
    ansver['msg'] = _('Your score is accepted.')
    return JsonResponse(ansver)


@require_POST
@check_ajax_auth
def change_cart_number(request):
    """
    """
    ansver = dict()
    try:
        root_ou   = request.user.departament
        des       = root_ou.get_descendants()
    except:
        ansver['error'] ='1'
        ansver['mes'] = _('Error: 101. Not set organization utint.')
        return JsonResponse(ansver)

    cart_id = request.POST.get('cart_id', '')
    cart_id = str2int(cart_id)
    cart_number = request.POST.get('cart_number', '')
    cart_number = cart_number.strip()

    if not len(cart_number):
        ansver['error'] ='1'
        ansver['mes'] = _('The number must not be empty.')
        return JsonResponse(ansver)

    try:
        m1 = CartridgeItem.objects.get(pk=cart_id)
    except CartridgeItem.DoesNotExist:
        ansver['error'] ='1'
        ansver['mes'] = _('Not found.')
        return JsonResponse(ansver)

    cart_index = m1.pk
    if not((m1.departament in des) or (m1.departament == request.user.departament)):
        ansver['error'] ='1'
        ansver['mes'] = _('An object with number %(cart_num)s belong to a different organizational unit.') % {'cart_num': cart_number}
        return JsonResponse(ansver)

    departament = m1.departament
    try:
        m2 = CartridgeItem.objects.filter(Q(cart_number=cart_number) & (Q(departament__in=des) | Q(departament=request.user.departament)))
    except CartridgeItem.DoesNotExist:
        ansver['error'] ='1'
        ansver['mes'] = _('Not found.')
        return JsonResponse(ansver)

    if m2.count():
        ansver['error'] ='1'
        ansver['mes'] = _('Number is already in use.')
        return JsonResponse(ansver)
    else:
        old_cart_number = m1.cart_number
        m1.cart_number = cart_number
        m1.save()
    
    sign_change_number.send(sender=None, cart_index=cart_index, old_number=old_cart_number, new_number=cart_number, request=request)
    ansver['error'] = '0'

    return JsonResponse(ansver)


@require_POST
@check_ajax_auth
def clear_basket_session(request):
    """Очистка сессионной корзины (добавление РМ через сканер штрихкода).
       Поэлементное удаление элементов из сессионной корзины, или очистка её целиком.
    """
    ansver = dict()

    selected = request.POST.getlist('selected[]', '')
    session_var = request.POST.get('session_var', '')
    select_all = request.POST.get('select_all', '')
    session_var = session_var.strip()
    empty_all = request.POST.get('empty_all', '')
    selected = [str2int(elem) for elem in selected]
    

    if session_var == 'add_cartridges_full_in_stock':
        session_data = request.session.get(session_var)
    elif session_var == 'add_cartridges_empty_in_stock':
        session_data = request.session.get(session_var)
    else:
        ansver['error'] = '1'
        ansver['text'] = _('Session varible not use.')
        return JsonResponse(ansver)
    
    if select_all == '1':
        request.session[session_var] = None
        ansver['error'] = '0'
        ansver['text'] = ''
        return JsonResponse(ansver)

    tmp_session_data = list()
    inx = 0
    for elem in session_data:
        if not(inx in selected): 
            tmp_session_data.append(elem)
        inx += 1

    request.session[session_var] = tmp_session_data
    ansver['error'] = '0'
    ansver['text'] = selected
    return JsonResponse(ansver)
