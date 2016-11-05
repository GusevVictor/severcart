# -*- coding:utf-8 -*-

import json
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import transaction
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from django.conf import settings
from common.helpers import is_admin
from common.cbv import CartridgesView
from common.helpers import BreadcrumbsPath
from .forms.add_items import AddItems
from .forms.add_items_from_barcode import AddItemsFromBarCodeScanner
from .forms.add_type import AddCartridgeType
from .forms.add_firm import FirmTonerRefillF
from .forms.tr_to_firm import TransfeToFirm, TransfeToFirmScanner
from .forms.tr_to_stock import MoveItemsToStockWithBarCodeScanner
from .forms.add_cartridge_name import AddCartridgeName
from .forms.comment import EditCommentForm
from .models import CartridgeType
from .models import CartridgeItem
from .models import OrganizationUnits
from .models import City as CityM
from .models import FirmTonerRefill
from .models import CartridgeItemName
from .helpers import str2int
from events.models import Events
from docs.models import SCDoc, RefillingCart
from storages.models import Storages
from .signals import sign_tr_filled_cart_to_stock

import logging
logger = logging.getLogger('simp')


@login_required
@never_cache
def dashboard(request):
    """Морда сайта. Отображает текущее состояние всего, что считаем.
    """
    context = {}
    try:
        root_ou   = request.user.departament
        des       = root_ou.get_descendants()
    except:
        context['full_on_stock']  = 0
        context['uses']           = 0
        context['empty_on_stock'] = 0
        context['filled']         = 0
        context['recycler_bin']   = 0
    else:
        filter_itms = lambda qy: CartridgeItem.objects.filter(qy)
        context['full_on_stock']  = filter_itms(Q(departament=root_ou) & Q(cart_status=1)).count()
        context['uses']           = filter_itms(Q(departament__in=des) & Q(cart_status=2)).count()
        context['empty_on_stock'] = filter_itms(Q(departament=root_ou) & Q(cart_status=3)).count()
        context['filled']         = filter_itms(Q(departament=root_ou) & Q(cart_status=4)).count()
        context['recycler_bin']   = filter_itms(Q(departament=root_ou) & (Q(cart_status=5) | Q(cart_status=6))).count()
    # формирование контекста топовых событий
    try:
        dept_id = request.user.departament.pk
    except AttributeError:
        dept_id = 0
    # формирование статистики
    import datetime
    cur_date  = timezone.now()
    use_day   = Events.objects.filter(departament=dept_id)
    use_day   = use_day.filter(event_type='TR')
    use_day   = use_day.filter(date_time__year=cur_date.year, date_time__month=cur_date.month, date_time__day=cur_date.day).count()
    
    bld_date  = datetime.datetime(cur_date.year, cur_date.month, 1)
    use_month = Events.objects.filter(departament=dept_id)
    use_month = use_month.filter(event_type='TR')
    use_month = use_month.filter(date_time__gte=bld_date).count()

    bld_date  = datetime.datetime(cur_date.year, 1, 1)
    use_year  = Events.objects.filter(departament=dept_id)
    use_year  = use_year.filter(event_type='TR')
    use_year  = use_year.filter(date_time__gte=bld_date).count()

    context['use_day']   = use_day
    context['use_month'] = use_month
    context['use_year']  = use_year

    # выполняем проверки безопасности используемого пароля,
    # если он не безопасен, то сообщаем об этом
    db_passwd = settings.DATABASES['default']['PASSWORD']
    if db_passwd == '123456':
        context['none_secure'] = True
    return render(request, 'index/dashboard.html', context)


class Stock(CartridgesView):
    """Списки заправленных, новых картриджей на складе
    """
    @method_decorator(login_required)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(Stock, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        super(Stock, self).get(*args, **kwargs)
        self.context['view'] = 'stock'
        self.all_items = self.all_items.filter(cart_status=1).filter(departament=self.request.user.departament)
        # для минимизации количества обращений к базе данных воспользуемся 
        # простиньким кэшом
        simple_cache = dict()
        i = 0 # итерируемая переменная для доступа по индексу
        # Внимание! Поля sklad_title и sklad_address являются искуственно
        # внедрёнными, в модели CartridgeItem их нет.
        for item in self.all_items:
            if simple_cache.get(item.sklad, 0):
                self.all_items[i].sklad_title = simple_cache.get(item.sklad)['title']
                self.all_items[i].sklad_address = simple_cache.get(item.sklad)['address']
            else:
                try:
                    sklad = Storages.objects.get(pk=item.sklad)
                except:
                    simple_cache[item.sklad] = {'title': '', 'address': ''}
                    self.all_items[i].sklad_title    = ''
                    self.all_items[i].sklad_address  = ''
                else:
                    simple_cache[item.sklad] =  {'title': sklad.title, 'address': sklad.address}
                    self.all_items[i].sklad_title    = sklad.title
                    self.all_items[i].sklad_address  = sklad.address
            i += 1

        page_size = self.items_per_page()
        self.context['size_perpage'] = page_size
        self.context['cartrjs'] = self.pagination(self.all_items, page_size)
        return render(request, 'index/stock.html', self.context)


@login_required
@never_cache
def add_cartridge_name(request):
    back = BreadcrumbsPath(request).before_page(request)
    if request.method == 'POST':
        form_obj = AddCartridgeName(request.POST)
        if form_obj.is_valid():
            data_in_post = form_obj.cleaned_data
            cart_name = data_in_post.get('cart_itm_name','')
            cart_name = cart_name.strip()
            if CartridgeItemName.objects.filter(cart_itm_name__iexact=cart_name):
                # если имя расходника уже занято
                messages.error(request, _('%(cart_name)s already exists') % {'cart_name': cart_name})
            else:    
                # добавляем новый тип расходного материала
                form_obj.save()
                messages.success(request, _('%(cart_name)s success added') % {'cart_name': cart_name})
            return HttpResponseRedirect(request.path)
    else:
        form_obj = AddCartridgeName()
    return render(request, 'index/add_name.html', {'form': form_obj, 'back': back})


@login_required
@never_cache
def add_cartridge_item(request):
    """Обработку данных формы производим в ajax_add_session_items. Здесь 
       отображаем заполненную форму.
    """
    if not request.user.departament:
        return render(request, 'index/ou_not_set.html', dict())

    back = BreadcrumbsPath(request).before_page(request)
    current_day = str(timezone.now().day) +'/' + str(timezone.now().month) +'/' + str(timezone.now().year)
    form_obj = AddItems()
    
    form_obj.fields['set_date'].initial = current_day
    # отфильтровываем и показываем только договора поставки
    form_obj.fields['doc'].queryset = SCDoc.objects.filter(departament=request.user.departament).filter(doc_type=1)
    form_obj.fields['storages'].queryset = Storages.objects.filter(departament=request.user.departament)
    
    # выбор склада по умолчанию в выбранной организации
    default_sklad = Storages.objects.filter(departament=request.user.departament).filter(default=True)
    try:
        if default_sklad[0].pk:
            form_obj.fields['storages'].initial = default_sklad[0].pk
    except IndexError:
        # если склад по-умолчанию не выбран, то пропускаем выбор склада
        pass
    session_data = request.session.get('cumulative_list')
    if not session_data:
        # если в сессии нужные данные отсутствуют, то сразу рендерим форму
        return render(request, 'index/add_items.html', {'form': form_obj, 'session': '', 'back': back})
    
    session_data = json.loads(session_data)
    simple_cache = dict()
    list_names = CartridgeItemName.objects.all()
    for elem in list_names:
        simple_cache[elem.pk] = elem.cart_itm_name
    list_items = list()
    for elem in session_data:
        try:
           title = str(SCDoc.objects.get(pk=elem[1]))
        except SCDoc.DoesNotExist:
            title = ''
        
        acumulyator = str()
        # избвавляемся от лишних апострофов при конвертрировании массива чисел
        # в строку
        for items in elem[2]:
            acumulyator += str(items) + ', '
        list_items.append({'name': simple_cache.get(elem[0]), 
                           'numbers': acumulyator, 
                           'title': title})

    html = render_to_string('index/add_over_ajax.html', context={'list_items': list_items})
    return render(request, 'index/add_items.html', {'form': form_obj, 'session': html, 'back': back})


@login_required
@never_cache
def add_cartridge_from_barcode_scanner(request):
    """Добавление новых РМ с сканера штрих кодов.
    """
    if not request.user.departament:
        return render(request, 'index/ou_not_set.html', dict())
    context = dict()
    context['debug'] = False
    back = BreadcrumbsPath(request).before_page(request)
    current_day = str(timezone.now().day) +'/' + str(timezone.now().month) +'/' + str(timezone.now().year)
    form = AddItemsFromBarCodeScanner()
    form.fields['set_date'].initial = current_day
    
    # отфильтровываем и показываем только договора поставки
    form.fields['doc'].queryset = SCDoc.objects.filter(departament=request.user.departament).filter(doc_type=1)
    form.fields['storages'].queryset = Storages.objects.filter(departament=request.user.departament)
    # выбор склада по умолчанию в выбранной организации
    default_sklad = Storages.objects.filter(departament=request.user.departament).filter(default=True)
    try:
        if default_sklad[0].pk:
            form.fields['storages'].initial = default_sklad[0].pk
    except IndexError:
        # если склад по-умолчанию не выбран, то пропускаем выбор склада
        pass

    # считываем данные для сессии
    if request.session.get('add_cartridges_full_in_stock', False):
        # если в сессионной переменной уже что-то есть
        session_data = request.session.get('add_cartridges_full_in_stock')
        
    else:
        # если сессионная basket_to_transfer_firm пуста или её нет вообще
        session_data = list()

    context['list_items'] = session_data
    context['form'] = form
    context['back'] = back
    context['action_type'] = 'full'
    context['session_var'] = 'add_cartridges_full_in_stock'
    return render(request, 'index/add_cartridge_from_barcode_scanner.html', context)


@login_required
@never_cache
def add_empty_cartridge_from_barcode_scanner(request):
    """Добавление пустых РМ с сканера штрих кодов.
    """
    if not request.user.departament:
        return render(request, 'index/ou_not_set.html', dict())
    context = dict()
    context['debug'] = False
    back = BreadcrumbsPath(request).before_page(request)
    current_day = str(timezone.now().day) +'/' + str(timezone.now().month) +'/' + str(timezone.now().year)
    form = AddItemsFromBarCodeScanner()
    form.fields['set_date'].initial = current_day
    
    # отфильтровываем и показываем только договора поставки
    form.fields['doc'].queryset = SCDoc.objects.filter(departament=request.user.departament).filter(doc_type=1)
    form.fields['storages'].queryset = Storages.objects.filter(departament=request.user.departament)
    # выбор склада по умолчанию в выбранной организации
    default_sklad = Storages.objects.filter(departament=request.user.departament).filter(default=True)
    try:
        if default_sklad[0].pk:
            form.fields['storages'].initial = default_sklad[0].pk
    except IndexError:
        # если склад по-умолчанию не выбран, то пропускаем выбор склада
        pass

    # считываем данные для сессии
    if request.session.get('add_cartridges_empty_in_stock', False):
        # если в сессионной переменной уже что-то есть
        session_data = request.session.get('add_cartridges_empty_in_stock')
        
    else:
        # если сессионная basket_to_transfer_firm пуста или её нет вообще
        session_data = list()

    context['list_items'] = session_data
    context['form'] = form
    context['back'] = back
    context['action_type'] = 'empty'
    context['session_var'] = 'add_cartridges_empty_in_stock'
    #return render(request, 'index/add_cartridge_from_barcode_scanner.html', context)
    return render(request, 'index/add_empty_cartridge_from_barcode_scanner.html', context)


@login_required
@never_cache
def add_empty_cartridge(request):
    """Добавление пустых картриджей.
    """
    if not request.user.departament:
        return render(request, 'index/ou_not_set.html', dict())

    context         = {}
    back            = BreadcrumbsPath(request).before_page(request)
    current_day = str(timezone.now().day) +'/' + str(timezone.now().month) +'/' + str(timezone.now().year)
    context['back'] = back
    form_obj = AddItems()

    form_obj.fields['set_date'].initial = current_day
    # отфильтровываем и показываем только договора поставки
    form_obj.fields['doc'].queryset = SCDoc.objects.filter(departament=request.user.departament).filter(doc_type=1)
    form_obj.fields['storages'].queryset = Storages.objects.filter(departament=request.user.departament)
    # выбор склада по умолчанию в выбранной организации
    default_sklad = Storages.objects.filter(departament=request.user.departament).filter(default=True)
    try:
        if default_sklad[0].pk:
            form_obj.fields['storages'].initial = default_sklad[0].pk
    except IndexError:
        # если склад по-умолчанию не выбран, то пропускаем выбор склада
        pass
    
    context['form'] = form_obj
    session_data = request.session.get('empty_cart_list')
    if not session_data:
        # если в сессии нужные данные отсутствуют, то сразу рендерим форму
        return render(request, 'index/add_empty_cartridge.html', context)
    
    session_data = json.loads(session_data)
    simple_cache = dict()
    list_names = CartridgeItemName.objects.all()
    for elem in list_names:
        simple_cache[elem.pk] = elem.cart_itm_name
    list_items = list()
    for elem in session_data:
        try:
           title = str(SCDoc.objects.get(pk=elem[1]))
        except SCDoc.DoesNotExist:
            title = ''
        
        # избвавляемся от лишних апострофов при конвертрировании массива чисел
        # в строку
        acumulyator = str()
        for items in elem[2]:
            acumulyator += str(items) + ', '

        list_items.append({'name': simple_cache.get(elem[0]), 
                           'numbers': acumulyator, 
                           'title': title})

    context['session'] = render_to_string('index/add_over_ajax.html', context={'list_items': list_items})
    return render(request, 'index/add_empty_cartridge.html', context)


@login_required
@is_admin
@never_cache
def tree_list(request):
    """Работаем с структурой организации
    """
    context = dict()
    if request.method == 'POST':
        uid = request.POST.get('departament', '')  # старшее огр. подразделение 
        org_name = request.POST.get('name', '') 
        org_name = org_name.strip()
        try:
            uid = int(uid)
        except ValueError:
            uid = 0
        # проверям, есть ли такая корневая нода уже в базе
        if uid == 0: # добавление корневой ноды
            for node in OrganizationUnits.objects.root_nodes():
                if node.name == org_name:
                    context['error1'] = _('Organization unit %(org_name)s exist') % {'org_name': org_name}
                    break        
            else:
                # если ноды нет, добавляем
                OrganizationUnits.objects.create(name=org_name, parent=None)
                context['msg'] = _('Organization unit %(org_name)s create successfuly.') % {'org_name': org_name}

        if uid != 0:
            temp_name = OrganizationUnits.objects.get(pk=uid)
            for node in temp_name.get_descendants(include_self=True):
                # производим поиск ноды среди потомков поддерева
                if node.name == org_name:
                    context['error1']= _('Organization unit %(org_name)s exist') % {'org_name': org_name}
                    break
            else:
                # блок элсе выполняется если внутри цикла фор не было прерыание через брейк
                OrganizationUnits.objects.create(name=org_name, parent=temp_name)
                context['msg'] = _('Organization unit %(org_name)s create successfuly.') % {'org_name': org_name}
    else:
        pass
                    
    context['bulk'] = OrganizationUnits.objects.all()
    return render(request, 'index/tree_list.html', context)


@login_required
@never_cache
def add_type(request):
    """Добавление нового типа расходника, а также редактирование существующего
    """
    back = BreadcrumbsPath(request).before_page(request)
    cart_type_id = request.GET.get('id', '')
    if cart_type_id:
        try:
            cart_type_id = int(cart_type_id)
        except ValueError:
            cart_type_id = 0
        try:
            m1 =  CartridgeType.objects.get(pk=cart_type_id)
        except CartridgeType.DoesNotExist:
            raise Http404
        else:
            form_update = True
    else:
        form_update = False

    if request.method == 'POST':
        
        if form_update: 
            form_obj = AddCartridgeType(request.POST, update=form_update, initial={'cart_type': m1.cart_type, 'comment': m1.comment})
        else:
            form_obj = AddCartridgeType(request.POST, update=form_update)

        if form_obj.is_valid():
            data_in_post = form_obj.cleaned_data
            cart_type = data_in_post['cart_type']
            cart_type_comment = data_in_post['comment']
            if cart_type_id:
                m1.cart_type=cart_type
                m1.comment=cart_type_comment
                m1.save()
                messages.success(request, _('%(cart_type)s success save') % {'cart_type': cart_type})
            else:
                m1 = CartridgeType(cart_type=cart_type, comment=cart_type_comment)
                m1.save()
                messages.success(request, _('New type %(cart_type)s success added') % {'cart_type': cart_type})
            return HttpResponseRedirect(request.path)
        else:
            pass
    else:
        if cart_type_id:
            form_obj = AddCartridgeType(initial={'cart_type': m1.cart_type, 'comment': m1.comment}, update=form_update)
        else:
            form_obj = AddCartridgeType(update=form_update)
    return render(request, 'index/add_type.html', {'form': form_obj, 'cart_type_id': cart_type_id, 'back': back})


@login_required
@never_cache
def transfe_for_use(request):
    """Передача расходника в пользование.
    """
    context = dict()
    checked_cartr = request.GET.get('select', '')
    tmp = ''
    if checked_cartr:
        checked_cartr = checked_cartr.split('s')
        checked_cartr = [int(i) for i in checked_cartr]
        tmp = checked_cartr
        context['ids_list'] = ','.join([str(i) for i in tmp])
        tmp2 = []
        cartr_objs = list()
        # преобразовываем айдишники в условные номера
        # данная информация исключительно информативная
        for cart_id in checked_cartr:
            m1 = CartridgeItem.objects.get(pk=cart_id)
            # проверяем принадлежность перемещаемого РМ департаменту 
            # пользователя.
            if m1.departament == request.user.departament:
                tmp2.append(m1.cart_number)
                cartr_objs.append(m1)
        checked_cartr = str(tmp2)
        checked_cartr = checked_cartr[1:-1]
        context['checked_cartr'] = checked_cartr
        context['cartr_objs']    = cartr_objs
    
    get = lambda node_id: OrganizationUnits.objects.get(pk=node_id)
    root_ou   = request.user.departament
    children  = root_ou.get_family()
    children  = children[1:] # исключаем последний элемент
    context['bulk'] = children
    return render(request, 'index/transfe_for_use.html', context)


class Use(CartridgesView):
    """Списки заправленных, новых картриджей на складе
    """
    @method_decorator(login_required)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(Use, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        super(Use, self).get(*args, **kwargs)
        self.context['view'] = 'use'
        try:
            root_ou   = self.request.user.departament
            children  = root_ou.get_family()
        except AttributeError:
            children = ''
        self.all_items = self.all_items.filter(departament__in=children).filter(cart_status=2)
        page_size = self.items_per_page()
        self.context['size_perpage'] = page_size
        self.context['cartrjs'] = self.pagination(self.all_items, page_size)
        return render(request, 'index/use.html', self.context)


class Empty(CartridgesView):
    """Списки заправленных, новых картриджей на складе
    """
    @method_decorator(login_required)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(Empty, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        super(Empty, self).get(*args, **kwargs)
        self.context['view'] = 'empty'
        root_ou = self.request.user.departament
        self.all_items = self.all_items.filter( Q(departament=root_ou) & Q(cart_status=3) )
        # для минимизации количества обращений к базе данных воспользуемся 
        # простиньким кэшом
        simple_cache = dict()
        i = 0 # итерируемая переменная для доступа по индексу
        # Внимание! Поля sklad_title и sklad_address являются искуственно
        # внедрёнными, в модели CartridgeItem их нет.
        for item in self.all_items:
            if simple_cache.get(item.sklad, 0):
                self.all_items[i].sklad_title = simple_cache.get(item.sklad)['title']
                self.all_items[i].sklad_address = simple_cache.get(item.sklad)['address']
            else:
                try:
                    sklad = Storages.objects.get(pk=item.sklad)
                except:
                    simple_cache[item.sklad] = {'title': '', 'address': ''}
                    self.all_items[i].sklad_title    = ''
                    self.all_items[i].sklad_address  = ''
                else:
                    simple_cache[item.sklad] =  {'title': sklad.title, 'address': sklad.address}
                    self.all_items[i].sklad_title    = sklad.title
                    self.all_items[i].sklad_address  = sklad.address
            i += 1

        page_size = self.items_per_page()
        self.context['size_perpage'] = page_size
        self.context['cartrjs'] = self.pagination(self.all_items, page_size)
        return render(request, 'index/empty.html', self.context)


@login_required
@never_cache
def toner_refill(request):
    """Список контрагентов, которым производим передачу РМ на заправку.
    """
    BreadcrumbsPath(request)
    city_id = request.GET.get('city', '')
    cities = CityM.objects.all()

    try:
        city_id = int(city_id)
    except ValueError:
        city_id = 0

    city = ""
    if city_id != 0:
        try:
            city = CityM.objects.get(pk=city_id)
        except CityM.DoesNotExist:
            raise Http404

    if city:
        firms = FirmTonerRefill.objects.filter(firm_city=city)
    else:
        firms = FirmTonerRefill.objects.all()
    # завершаем работу с пагинацией
    new_list = [{'id': 0, 'city_name': _('Select all')}]
    for i in cities:
        tmp_dict = {'id': i.id, 'city_name': i.city_name}
        new_list.append(tmp_dict)

    cities = None
    if city_id:
        city_url_parametr = '?city=' + str(city_id) + '&'
    else:
        city_url_parametr = '?'
    return render(request, 'index/toner_refill.html', {'cities': new_list,
                                                       'firms': firms,
                                                       'select': city_id,
                                                       'city_url': city_url_parametr,
                                                       })


@login_required
@never_cache
def add_firm(request):
    """
    """
    back = BreadcrumbsPath(request).before_page(request)
    if request.method == 'POST':
        form_obj = FirmTonerRefillF(request.POST)
        if form_obj.is_valid():
            data_in_post = form_obj.cleaned_data
            m1 = FirmTonerRefill(firm_name=data_in_post['firm_name'],
                                 firm_city=data_in_post['firm_city'],
                                 firm_contacts=data_in_post['firm_contacts'],
                                 firm_address=data_in_post['firm_address'],
                                 firm_comments=data_in_post['firm_comments'], )
            m1.save()
            messages.success(request, _('Firm "%(firm_name)s" success added.') % {'firm_name': data_in_post['firm_name']})
    else:
        form_obj = FirmTonerRefillF()
    return render(request, 'index/add_firm.html', {'form': form_obj, 'back': back})


@login_required
@never_cache
def edit_firm(request):
    """
    """
    back = BreadcrumbsPath(request).before_page(request)
    firm_id = request.GET.get('select', '')
    firm_id = firm_id.strip()
    if firm_id:
        try:
            firm_id = int(firm_id)
        except ValueError:
            firm_id = 0
    else:
        firm_id = 0

    if request.method == 'POST':
        form_obj = FirmTonerRefillF(request.POST)
        if form_obj.is_valid():
            data_in_post = form_obj.cleaned_data
            m1 = FirmTonerRefill.objects.get(pk=firm_id)
            m1.firm_name = data_in_post['firm_name']
            m1.firm_city = data_in_post['firm_city']
            m1.firm_contacts = data_in_post['firm_contacts']
            m1.firm_address = data_in_post['firm_address']
            m1.firm_comments = data_in_post['firm_comments']
            m1.save(update_fields=[
                'firm_name',
                'firm_city',
                'firm_contacts',
                'firm_address',
                'firm_comments'])

            return HttpResponseRedirect(reverse('index:toner_refill'))

    try:
        firm = FirmTonerRefill.objects.get(pk=firm_id)
    except FirmTonerRefill.DoesNotExist:
        raise Http404

    form_obj = FirmTonerRefillF(initial={
        'firm_name': firm.firm_name,
        'firm_city': firm.firm_city,
        'firm_contacts': firm.firm_contacts,
        'firm_address': firm.firm_address,
        'firm_comments': firm.firm_comments})
    return render(request, 'index/edit_firm.html', {'firm': firm, 'form': form_obj, 'back': back})


class At_work(CartridgesView):
    """Список картриджей находящихся на заправке.
    """
    @method_decorator(login_required)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(At_work, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        super(At_work, self).get(*args, **kwargs)
        self.context['view'] = 'at_work'
        self.all_items = self.all_items.filter(Q(cart_status=4) & Q(departament=self.request.user.departament))
        page_size = self.items_per_page()
        self.context['size_perpage'] = page_size
        self.context['cartrjs'] = self.pagination(self.all_items, page_size)
        return render(request, 'index/at_work.html', self.context)


def from_firm_to_stock_with_barcode(request):
    """Возврат РМ из обслуживающей фирмы обратно на склад.
    """
    context = dict()
    MYDEBUG = False
    context['mydebug'] = MYDEBUG
    back = BreadcrumbsPath(request).before_page(request)
    form = MoveItemsToStockWithBarCodeScanner()
    #form.fields['storages'].queryset = Storages.objects.filter(departament=request.user.departament)
    # выбор склада по умолчанию в выбранной организации
    #default_sklad = Storages.objects.filter(departament=request.user.departament).filter(default=True)
    #try:
    #    if default_sklad[0].pk:
    #        form.fields['storages'].initial = default_sklad[0].pk
    #except IndexError:
        # если склад по-умолчанию не выбран, то пропускаем выбор склада
    #    pass

    # заполняем таблицу перемещаемых РМ значениями из сессии
    # это пригодится на случай случайной перезагрузки страницы пользователем
    session_data = request.session.get('basket_to_transfer_stock', False)
    show_list = list()
    if not session_data:
        session_data = []
    initial_numbers = str()
    for cart_pk in session_data:
        initial_numbers += str(cart_pk) + ', '
        try:
            cart_obj = CartridgeItem.objects.get(pk=cart_pk)
        except CartridgeItem.DoesNotExist:
            cart_obj = dict()
        else:
            cart_obj = {'pk': cart_obj.pk, 'cart_number': cart_obj.cart_number, 'cart_name': str(cart_obj.cart_itm_name)}
            show_list.append(cart_obj)

    form.fields['numbers'].initial = initial_numbers
    context['show_list'] = show_list
    context['back'] = back
    context['form'] = form
    return render(request, 'index/from_firm_to_stock_with_barcode.html', context)


class Basket(CartridgesView):
    """Список картриджей на выброс.
    """
    @method_decorator(login_required)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(Basket, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        super(Basket, self).get(*args, **kwargs)
        self.context['view'] = 'basket'
        self.all_items = self.all_items.filter( (Q(cart_status=5) | Q(cart_status=6)) & Q(departament=self.request.user.departament) )
        page_size = self.items_per_page()
        self.context['size_perpage'] = page_size
        self.context['cartrjs'] = self.pagination(self.all_items, page_size)
        return render(request, 'index/basket.html', self.context)


@login_required
@never_cache
def transfer_to_firm(request):
    """Передача расходных материалов на заправку.
    """
    context = dict()
    checked_cartr = request.GET.get('select', '')
    if checked_cartr:
        checked_cartr = checked_cartr.split('s')
        checked_cartr = [int(i) for i in checked_cartr]
        # преобразовываем айдишники в условные номера
        transfe_objs = list()
        for cart_id in checked_cartr:
            m1 = CartridgeItem.objects.get(pk=cart_id)
            # проверяем принадлежность перемещаемого РМ департаменту 
            # пользователя.
            if m1.departament == request.user.departament:
                transfe_objs.append(m1)
        
        checked_cartr = str(checked_cartr)  # преобразуем список в строку
        checked_cartr = checked_cartr[1:-1] # убираем угловые скобочки
    else:
        # если кто-то зашел на страницу не выбрав расходники
        return HttpResponseRedirect(reverse('index:empty'))
    form = TransfeToFirm(initial = {'numbers': checked_cartr})
    form.fields['doc'].queryset = SCDoc.objects.filter(departament=request.user.departament).filter(doc_type=2)
    context['form'] = form
    context['checked_cartr'] = checked_cartr
    context['transfe_objs'] = transfe_objs
    return render(request, 'index/transfer_to_firm.html', context)


@login_required
@never_cache
def transfer_to_firm_with_scanner(request):
    """Составление списка перемещаемых картриджей на заправку с 
       помощью сканера ШК
    """
    context = dict()
    form = TransfeToFirmScanner()
    form.fields['doc'].queryset = SCDoc.objects.filter(departament=request.user.departament).filter(doc_type=2)
        
    if request.session.get('basket_to_transfer_firm', False):
        # если в сессионной переменной уже что-то есть
        session_data = request.session.get('basket_to_transfer_firm')
    else:
        # если сессионная basket_to_transfer_firm пуста или её нет вообще
        session_data = [ ]

    sessions_objects = list()
    if session_data:
        for item_pk in session_data:
            try:   
                item_pk = int(item_pk)
            except ValueError:
                item_pk = 1
            cartridge= CartridgeItem.objects.get(pk=item_pk)
            tmp_str = str(cartridge.cart_number)
            if len(tmp_str) >= settings.TRLEN:
                tmp_str = tmp_str[0:settings.TRLEN] + '...'
            sessions_objects.append({'pk': cartridge.pk, 'name': str(cartridge.cart_itm_name), 'number':tmp_str, 'title': cartridge.cart_number})

    context['show_remove_session_button'] = False
    if len(sessions_objects) >= 1:
        context['show_remove_session_button'] = True
    
    # инициализируем поле numbers значениями сессионной переменной, 
    # если пользователь произвёл перезагрузку страницы. 
    form.fields['numbers'].initial = str(session_data)[1:-1] 
    context['sessions_objects'] = sessions_objects        
    context['form'] = form
    context['mydebug'] = False
    return render(request, 'index/transfer_to_firm_with_scanner.html', context)


@login_required
@never_cache
def from_firm_to_stock(request):
    """Возврашаем заправленные расходники обратно на базу.
    """
    back = BreadcrumbsPath(request).before_page(request)
    checked_cartr = request.GET.get('select', '')
    tmp = ''
    list_cart = []
    if checked_cartr:
        checked_cartr = checked_cartr.split('s')
        checked_cartr = [int(i) for i in checked_cartr]
        tmp = checked_cartr
        for cart_id in tmp:
            list_cart.append(CartridgeItem.objects.get(pk=cart_id))
        list_length = len(list_cart) 
        # преобразуем список в строку, для корректного отображения на html странице
        checked_cartr = str(checked_cartr)
        checked_cartr = checked_cartr[1:-1]
    else:
        # если кто-то зашел на страницу не выбрав расходники
        return HttpResponseRedirect(reverse('index:at_work'))        

    if request.method == 'POST':
        list_cplx = []
        with transaction.atomic():
            for inx in tmp:
                m1 = CartridgeItem.objects.get(pk=inx)
                # проверяем принадлежность перемещаемого РМ департаменту 
                # пользователя.
                firm = str(m1.filled_firm)
                if m1.departament == request.user.departament:
                    filled_firm = firm
                    m1.filled_firm = None
                    m1.cart_status = 1
                    m1.cart_date_change = timezone.now()
                    m1.vote = False
                    m1.cart_number_refills = int(m1.cart_number_refills) + 1
                    m1.save()
                    repair_actions = request.POST.getlist('cart_'+str(inx))
                    list_cplx.append((m1.id, str(m1.cart_itm_name), filled_firm, repair_actions, m1.cart_number))
                
        if list_cplx:
            sign_tr_filled_cart_to_stock.send(sender=None, list_cplx=list_cplx, request=request)

        # очищаем сессионную переменную 'basket_to_transfer_stock'
        try:
            request.session.get('basket_to_transfer_stock', False)
        except:
            request.session['basket_to_transfer_stock'] = None
        else:
            request.session['basket_to_transfer_stock'] = None

        # генерируем акт возвращения РМ
        jsoning_list = []
        for inx in tmp:
            cart_number = CartridgeItem.objects.get(pk=inx).cart_number
            cart_name   = CartridgeItem.objects.get(pk=inx).cart_itm_name
            repair_actions = request.POST.getlist('cart_'+str(inx))
            money_per_one = request.POST.getlist('cart_money'+str(inx))
            jsoning_list.append([cart_number, str(cart_name), repair_actions, money_per_one])
        jsoning_list = json.dumps(jsoning_list)
        
        
        # генерируем номер акта передачи на основе даты и его порядкового номера
        sender_acts = RefillingCart.objects.filter(departament=request.user.departament).count()
        # генерируем новый номер
        if sender_acts:
            act_number   = sender_acts + 1
            act_number   = str(timezone.now().year) + '_' + str(sender_acts)
        else:
            act_number   = str(timezone.now().year) + '_1'

        # сохраняем в БД акт передачи РМ на заправку
        act_doc = RefillingCart(
                                doc_type     = 2,        # документ возвращения с заправки
                                number       = act_number,
                                date_created = timezone.now(),
                                firm         = firm,
                                user         = str(request.user),
                                json_content = jsoning_list,
                                #money        = price,
                                departament  = request.user.departament
                               )
        act_doc.save()

        return HttpResponseRedirect(reverse('index:at_work'))
    return render(request, 'index/from_firm_to_stock.html', {'checked_cartr': checked_cartr, 
                                                            'list_cart': list_cart, 
                                                            'list_length': list_length, 
                                                            'back': back})


def bad_browser(request):
    """Сообщение о необходимости обновить браузер.
    """
    return render(request, 'index/bad_browser.html')


@login_required
@never_cache
def edit_cartridge_comment(request):
    """Добавляем комментарий к картриджу.
    """
    item_id = request.GET.get('id', '')
    back    = BreadcrumbsPath(request).before_page(request)
    try:
        item_id = int(item_id)
    except ValueError:
        item_id = 0
    try:
        cartridge_object = CartridgeItem.objects.get(pk=item_id)
    except CartridgeItem.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = EditCommentForm(data=request.POST)
        if form.is_valid():
            cartridge_object.comment = form.cleaned_data.get('comment')
            cartridge_object.save()
            return HttpResponseRedirect(back)
    else:
        comment = cartridge_object.comment
        form = EditCommentForm(initial = {'comment': comment})
    return render(request, 'index/edit_cartridge_comment.html', {'form': form, 'back': back})


def robots_txt(request):
    """Возвращает содержимое robots.txt
    """
    text = 'User-agent: *\nAllow: /\n'
    response = HttpResponse(text)
    response['Content-Type'] = 'text/plain'
    return response


def favicon_ico(request):
    """Возвращает содержимое favicon.ico
    """
    import os
    icof = os.path.join(settings.BASE_DIR, 'static', 'img', 'favicon.ico')

    if os.path.isfile(icof):
        with open(icof, 'rb') as fp:
            content = fp.read()
    else:
        content = ''

    response = HttpResponse(content)
    response['Content-Type'] = 'image/x-icon'
    return response


@login_required
@never_cache
def evaluate_service(request):
    """Оценить качество обслуживания контрагентом.
    """
    context = dict()
    context['back'] = BreadcrumbsPath(request).before_page(request)
    cart_id = request.GET.get('id', 0)
    cart_id = str2int(cart_id)
    try:
        node = CartridgeItem.objects.get(pk=cart_id)
    except CartridgeItem.DoesNotExist:
        raise Http404
    # проверяем принадлежность перемещаемого РМ департаменту
    # пользователя.
    try:
        root_ou   = request.user.departament
        des       = root_ou.get_descendants()
    except:
        pass

    if  node.vote:
        context['error'] = True
        context['msg'] = _('Work has already estimated.')
        return render(request, 'index/evaluate_service.html', context)
        
    if node.departament in des:
        obj_evs = Events.objects.filter(departament=request.user.departament.pk).filter(cart_number=node.cart_number)
        obj_evs = obj_evs.filter(event_type='TF').order_by('-pk')
        if obj_evs:
            context['error'] = False
            firm_name = obj_evs[0].event_firm
            context['cart_id'] = node.pk
            context['cart_number'] = node.cart_number
            tmp_list = firm_name.split(':')
            context['firm'] = tmp_list[0]
            if len(tmp_list) == 1:
                # оставлена возможнасть поиска по имени для старых релизов программы
                try:    
                    context['firm_id'] = FirmTonerRefill.objects.get(firm_name=firm_name).pk
                except:
                    context['firm_id'] = -1

            elif len(tmp_list) == 2:
                firm_id = str2int(tmp_list[1])
                try:    
                    context['firm_id'] = FirmTonerRefill.objects.get(pk=firm_id).pk
                except:
                    context['firm_id'] = -1
            else:
                context['firm_id'] = -1
                                
        else:
            context['error'] = True
            context['msg'] = _('An object with number %(cart_num)s is not transmitted to the service.') % {'cart_num': node.cart_number}

    else:
        context['error'] = True
        context['msg'] = _('An object with number %(cart_num)s belong to a different organizational unit.') % {'cart_num': node.cart_number}

    return render(request, 'index/evaluate_service.html', context)
