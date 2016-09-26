# -*- coding:utf-8 -*-

import json
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
from events.helpers import events_decoder
from index.models import ( City, 
                           CartridgeItem, 
                           OrganizationUnits, 
                           CartridgeItemName, 
                           FirmTonerRefill,
                           STATUS )
from index.helpers import check_ajax_auth, LastNumber
from index.signals import ( sign_turf_cart, 
                            sign_add_full_to_stock, 
                            sign_tr_empty_cart_to_stock,
                            sign_tr_cart_to_basket, 
                            sign_add_empty_to_stock, 
                            sign_tr_cart_to_uses, 
                            sign_tr_empty_cart_to_firm, ) 
from index.forms.add_items import AddItems
from index.forms.add_items_from_barcode import AddItemsFromBarCodeScanner
from index.forms.tr_to_firm import TransfeToFirm
from docs.models import SCDoc, RefillingCart


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
        tumbler = request.POST.get('tumbler', 0)
        try:
            tumbler = int(tumbler)
        except ValueError:
            tumbler = 0

        # чтобы не плодить лишние сущности зделано одно вью для добавления разных картриджей
        if cart_type == 'full':
            cart_status = 1
        elif cart_type == 'empty':
            cart_status = 3
        else:
            tmp_dict['error'] ='1'
            tmp_dict['mes']   = _('Error in attrib "data" in input button add_item')
            return JsonResponse(tmp_dict)

        def search_number(cart_number):
            """Функция для поиска дублей номеров внутри представительства.
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

        list_cplx    = list()
        if tumbler:
            # если переключатель ручного ввода номера включен
            cart_number = request.POST.get('cart_number')
            cart_number = cart_number.strip()
            # далее выполняем проверку на дубли, только внутри своего представительства
            cart_items = search_number(cart_number)

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
            while len(search_number(cart_number)):
                cart_number += 1

        # Добавляем картриджи в БД
        with transaction.atomic():
            for i in range(cart_count):
                m1 = CartridgeItem(sklad=storages,
                                   cart_number=str(cart_number),
                                   cart_itm_name=data_in_post.get('cartName'),
                                   cart_date_added=timezone.now(),
                                   cart_date_change=timezone.now(),
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
                    while len(search_number(cart_number)):
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


@check_ajax_auth
def ajax_add_session_items_from_barcode(request):
    """Добавляем картриджи на склад с помощью сканера штрих кодов.
    """
    if request.method != 'POST':
        return HttpResponse('<h1>' + _('Only use POST requests!') + '</h1>')
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
        cart_type    = request.POST.get('cart_type')
        cart_doc_id  = data_in_post.get('doc')

        # чтобы не плодить лишние сущности зделано одно вью для добавления разных картриджей
        if cart_type == 'full':
            cart_status = 1
        elif cart_type == 'empty':
            cart_status = 3
        else:
            context['error'] ='1'
            context['mes']   = _('Error in attrib "data" in input button add_item')
            return JsonResponse(context)

        list_cplx = list()
        # Добавляем отсканированный картридж в БД
        with transaction.atomic():
            m1 = CartridgeItem(sklad=storages,
                               cart_number=str(cart_number),
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
        
        context['mes'] = _('Cartridge %(cart_number)s successfully added.') % {'cart_number': cart_number}
        # запускаем сигнал добавления событий
        if cart_status == 1:
            sign_add_full_to_stock.send(sender=None, list_cplx=list_cplx, request=request)
        elif cart_status == 3:
            sign_add_empty_to_stock.send(sender=None, list_cplx=list_cplx, request=request)
        else:
            pass

    return JsonResponse(context)    

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
                                            firm=str(firm)
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
    list_cplx = list()
    show_numbers = list() # используется для информационных сообщений
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
        for inx in installed:
            # проверяем принадлежность перемещаемого РМ департаменту 
            # пользователя.
            if m1.departament == request.user.departament:
                m1 = CartridgeItem.objects.get(pk=inx)
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
        price        = data_in_post.get('price')
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
                                money        = price,
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

