# -*- coding:utf-8 -*-

import json
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.db.models import Q
from .forms.add_cartridge_name import AddCartridgeName
from .forms.add_items import AddItems
from .forms.add_city import CityF
from .forms.add_type import AddCartridgeType
from .forms.add_firm import FirmTonerRefillF
from .forms.comment import EditCommentForm
from .models import CartridgeType
from accounts.models import AnconUser
from django.contrib.auth.models import User
from .models import CartridgeItem
from .models import OrganizationUnits
from .models import City as CityM
from .models import FirmTonerRefill
from .models import CartridgeItemName
from .helpers import recursiveChildren, check_ajax_auth
from .helpers import Dashboard
from .sc_paginator import sc_paginator
from .signals import sign_add_full_to_stock

import logging
logger = logging.getLogger('simp')

@login_required
def dashboard(request):
    """Морда сайта. Отображает текущее состояние всего, что считаем.
    """
    try:
        root_ou   = request.user.departament
        children  = root_ou.get_children()
    except AttributeError:
        children = ''
    filter_itms = lambda qy: CartridgeItem.objects.filter(qy)
    context = {}
    context['full_on_stock']  = filter_itms(Q(departament=root_ou) & Q(cart_status=1)).count() #row.full_on_stock
    context['uses']           = filter_itms(Q(departament__in=children) & Q(cart_status=2)).count() #row.uses
    context['empty_on_stock'] = filter_itms(Q(departament=root_ou) & Q(cart_status=3)).count() #row.empty_on_stock
    context['filled']         = filter_itms(Q(departament=root_ou) & Q(cart_status=4)).count() #row.filled
    context['recycler_bin']   = filter_itms(Q(departament=root_ou) & (Q(cart_status=5) | Q(cart_status=6))).count()# row.recycler_bin
    return render(request, 'index/dashboard.html', context)


@login_required
def stock(request):
    """
    """
    all_items = CartridgeItem.objects.filter(departament=request.user.departament).filter(cart_status=1).order_by('pk')
    cartridjes = sc_paginator(all_items, request)
    return render(request, 'index/stock.html', {'cartrjs': cartridjes})


@login_required
def add_cartridge_name(request):
    if request.method == 'POST':
        form_obj = AddCartridgeName(request.POST)
        if form_obj.is_valid():
            data_in_post = form_obj.cleaned_data
            cart_name = data_in_post.get('cart_itm_name','')
            cart_name = cart_name.strip()
            if CartridgeItemName.objects.filter(cart_itm_name__iexact=cart_name):
                # если имя расходника уже занято
                messages.error(request, '%s уже существует.' % (cart_name,))
            else:    
                # добавляем новый тип расходного материала
                form_obj.save()
                messages.success(request, '%s успешно добавлен.' % (cart_name,))
            return HttpResponseRedirect(request.path)

    else:
        form_obj = AddCartridgeName()
    return render(request, 'index/add_name.html', {'form': form_obj})


@login_required
def add_cartridge_item(request):
    if request.method == 'POST':
        form_obj = AddItems(request.POST)
        if form_obj.is_valid():
            # добавляем новый тип расходного материала
            data_in_post = form_obj.cleaned_data
            count_items  = int(data_in_post['cartCount'])
            cart_type    = str(data_in_post['cartName'])
            # получаем объект текущего пользователя
            for i in range(count_items):
                m1 = CartridgeItem(cart_itm_name=data_in_post['cartName'],
                                   cart_date_added=timezone.now(),
                                   cart_number_refills=0,
                                   departament=request.user.departament,
                                   )
                m1.save()
                sign_add_full_to_stock.send(sender=None, num=m1.id,
                                            cart_type=cart_type,
                                            user=str(request.user),
                                            request=request)
            if count_items == 1:
                tmpl_message = 'Расходник %s успешно добавлен.'
            elif count_items > 1:
                tmpl_message = 'Расходники %s успешно добавлены.'
            messages.success(request, tmpl_message % (cart_type,))
            return HttpResponseRedirect(request.path)

    else:
        form_obj = AddItems()
    return render(request, 'index/add_items.html', {'form': form_obj})


@login_required
def tree_list(request):
    """Работаем с структурой организации
    """
    error1 = ''
    if request.method == 'POST':
        uid = request.POST.get('departament', '')        
        org_name = request.POST.get('name', '') 
        try:
            uid = int(uid)
        except ValueError:
            uid = 0

        # проверям, есть ли такая корневая нода уже в базе
        if uid == 0:
            for node in OrganizationUnits.objects.root_nodes():
                if node == org_name:
                    error1 = 'Организационная единица %s уже существует' % (org_name,)
                    break        
            else:
                # если ноды нет, добавляем
                rock = OrganizationUnits.objects.create(name=org_name)
        
        if uid != 0:
            temp_name = OrganizationUnits.objects.get(pk=uid)
            if temp_name.is_root_node():
                OrganizationUnits.objects.create(name=org_name, parent=temp_name)
            else:    
                for node in temp_name.get_children():
                    if node == org_name:
                        error1 = 'Организационная единица %s уже существует' % (org_name,)
                        break
                else:
                    rn = OrganizationUnits.objects.get(pk=uid)
                    OrganizationUnits.objects.create(name=org_name, parent=rn)        
            
    bulk = OrganizationUnits.objects.all()
    return render(request, 'index/tree_list.html', {'bulk': bulk, 'error1': error1})


@login_required
def add_type(request):
    """

    """
    if request.method == 'POST':
        form_obj = AddCartridgeType(request.POST)
        if form_obj.is_valid():
            data_in_post = form_obj.cleaned_data
            cart_type = data_in_post['cart_type']
            cart_type = cart_type.strip()
            if CartridgeType.objects.filter(cart_type__iexact=cart_type):
                # регистронезвисимый поиск.
                messages.error(request, 'Новый тип "%s" уже существует!' % (cart_type))
            else:    
                m1 = CartridgeType(cart_type=cart_type)
                m1.save()
                messages.success(request, 'Новый тип "%s" успешно добавлен.' % (cart_type))
            return HttpResponseRedirect(request.path)
    else:
        form_obj = AddCartridgeType()
    return render(request, 'index/add_type.html', {'form': form_obj})


@login_required
def transfe_for_use(request):
    """

    """
    checked_cartr = request.GET.get('select', '')
    tmp = ''
    if checked_cartr:
        checked_cartr = checked_cartr.split('s')
        checked_cartr = [int(i) for i in checked_cartr]
        tmp = checked_cartr
        checked_cartr = str(checked_cartr)
        checked_cartr = checked_cartr[1:-1]
    
    get = lambda node_id: OrganizationUnits.objects.get(pk=node_id)
    root_ou   = request.user.departament
    children  = root_ou.get_children()

    if request.method == 'POST':
        data_in_post = request.POST
        parent_id = data_in_post['par_id']
        parent_id = int(parent_id)

        for inx in tmp:
            m1 = CartridgeItem.objects.get(pk=inx)
            m1.cart_status = 2 # объект находится в пользовании
            m1.departament = get(parent_id)
            m1.save(update_fields=['departament', 'cart_status'])
        
        return HttpResponseRedirect(reverse('stock'))
    return render(request, 'index/transfe_for_use.html', {'checked_cartr': checked_cartr, 'bulk': children})


@login_required
def transfer_to_stock(request):
    """

    """
    checked_cartr = request.GET.get('select', '')
    tmp = ''
    if checked_cartr:
        checked_cartr = checked_cartr.split('s')
        checked_cartr = [int(i) for i in checked_cartr]
        tmp = checked_cartr
        checked_cartr = str(checked_cartr)
        checked_cartr = checked_cartr[1:-1]

    if request.method == 'POST':
        for inx in tmp:
            m1 = CartridgeItem.objects.get(pk=inx)
            m1.cart_status = 3     # пустой объект на складе
            m1.departament = request.user.departament
            m1.save(update_fields=['departament', 'cart_status'])
        
        return HttpResponseRedirect("/use/")
    return render(request, 'index/transfer_for_stock.html', {'checked_cartr': checked_cartr})


@login_required
def use(request):
    """Задействованные расходники.
    """
    try:
        root_ou   = request.user.departament
        children  = root_ou.get_children()
    except AttributeError:
        children = ''
    all_items = CartridgeItem.objects.filter(departament__in=children).filter(cart_status=2)
    cartridjes = sc_paginator(all_items, request)
    return render(request, 'index/use.html', {'cartrjs': cartridjes})


@login_required
def empty(request):
    """Список пустых картриджей.
    """
    root_ou = request.user.departament
    items = CartridgeItem.objects.filter( Q(departament=root_ou) & Q(cart_status=3) )
    items = sc_paginator(items, request)
    return render(request, 'index/empty.html', {'cartrjs': items})


@login_required
def toner_refill(request):
    """

    """

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

    # работаем с пагинацией
    firms = sc_paginator(firms, request)
    # завершаем работу с пагинацией

    new_list = [{'id': 0, 'city_name': 'Выбрать все'}]
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
                                                       'city_url': city_url_parametr
                                                       })


@login_required
def add_city(request):
    """

    """
    if request.method == 'POST':
        form_obj = CityF(request.POST)
        if form_obj.is_valid():
            data_in_post = form_obj.cleaned_data
            m1 = CityM(city_name=data_in_post['city_name'])
            m1.save()
            return HttpResponseRedirect(reverse('index.views.toner_refill'))
    else:
        form_obj = CityF()
    return render(request, 'index/add_city.html', {'form': form_obj})


@login_required
def add_firm(request):
    """

    """

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
            return HttpResponseRedirect('index.views.toner_refill')
    else:
        form_obj = FirmTonerRefillF()
    return render(request, 'index/add_firm.html', {'form': form_obj})


@login_required
def edit_firm(request):
    """

    """
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
            all = form_obj.cleaned_data
            m1 = FirmTonerRefill.objects.get(pk=firm_id)
            m1.firm_name = all['firm_name']
            m1.firm_city = all['firm_city']
            m1.firm_contacts = all['firm_contacts']
            m1.firm_address = all['firm_address']
            m1.firm_comments = all['firm_comments']
            m1.save(update_fields=[
                'firm_name',
                'firm_city',
                'firm_contacts',
                'firm_address',
                'firm_comments'])

            return HttpResponseRedirect(reverse('index.views.toner_refill'))

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
    return render(request, 'index/edit_firm.html', {'firm': firm, 'form': form_obj})


@login_required
def del_firm(request):
    """

    """
    firm_id = request.GET.get('select', '')
    firm_id = firm_id.strip()
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
        raise Http404

    if request.method == 'POST':
        id_in_post = request.POST.get('id', '')
        try:
            id_in_post = int(firm_id)
        except ValueError:
            id_in_post = 0

        try:
            firm = FirmTonerRefill.objects.get(pk=firm_id)
            firm.delete()
        except FirmTonerRefill.DoesNotExist:
            raise Http404

        return HttpResponseRedirect(reverse('index.views.toner_refill'))

    return render(request, 'index/del_firm.html', {'firm': firm})


@login_required
def manage_users(request):
    """
    """
    usr = AnconUser.objects.all()
    usr = sc_paginator(usr, request)
    return render(request, 'index/manage_users.html', {'urs': usr})


@login_required
def at_work(request):
    """Список картриджей находящихся на заправке.
    """
    items = CartridgeItem.objects.filter(cart_status=4)
    items = sc_paginator(items, request)
    return render(request, 'index/at_work.html', {'cartrjs': items})


@login_required
def basket(request):
    """Список картриджей на выброс.
    """
    items = CartridgeItem.objects.filter( Q(cart_status=5) | Q(cart_status=6) )
    items = sc_paginator(items, request)
    return render(request, 'index/basket.html', {'cartrjs': items})


@login_required
def transfe_to_basket(request):
    """Перемещаем расходники в корзинку.
    """
    checked_cartr = request.GET.get('select', '')
    action_type = request.GET.get('atype', '')
    
    if action_type == '5':
        # перемещаем заправленный картридж в корзину
        cart_status = 5
    elif action_type == '6':
        # перемещаем пустой картридж в корзину
        cart_status = 6
    else:
        raise Http404

    tmp = ''
    if checked_cartr:
        checked_cartr = checked_cartr.split('s')
        checked_cartr = [int(i) for i in checked_cartr]
        tmp = checked_cartr
        checked_cartr = str(checked_cartr)
        checked_cartr = checked_cartr[1:-1]
    
    if request.method == 'POST':
        for inx in tmp:
            m1 = CartridgeItem.objects.get(pk=inx)
            m1.cart_status = cart_status  # в корзинку картриджи  
            m1.save(update_fields=['cart_status'])
        
        return HttpResponseRedirect(reverse('stock'))
    return render(request, 'index/transfe_to_basket.html', {'checked_cartr': checked_cartr})


@login_required
def from_basket_to_stock(request):
    """Возвращаем обратно картридж из корзины на склад. Ну вдруг пользователь передумал.
    """
    checked_cartr = request.GET.get('select', '')
    tmp = ''
    if checked_cartr:
        checked_cartr = checked_cartr.split('s')
        checked_cartr = [int(i) for i in checked_cartr]
        tmp = checked_cartr
        checked_cartr = str(checked_cartr)
        checked_cartr = checked_cartr[1:-1]
    
    if request.method == 'POST':
        for inx in tmp:
            m1 = CartridgeItem.objects.get(pk=inx)
            if m1.cart_status == 5:
                m1.cart_status = 1  # возвращаем обратно на склад заполненным    
            elif m1.cart_status == 6:
                m1.cart_status = 3  # возвращаем обратно на склад пустым    
            else:
                raise Http404
            m1.save(update_fields=['cart_status'])
        return HttpResponseRedirect(reverse('basket'))
    return render(request, 'index/from_basket_to_stock.html', {'checked_cartr': checked_cartr})


@login_required
def transfer_to_firm(request):
    """Передача расходных материалов на заправку.
    """
    checked_cartr = request.GET.get('select', '')
    tmp = ''
    firms = FirmTonerRefill.objects.all()
    if checked_cartr:
        checked_cartr = checked_cartr.split('s')
        checked_cartr = [int(i) for i in checked_cartr]
        tmp = checked_cartr
        checked_cartr = str(checked_cartr)
        checked_cartr = checked_cartr[1:-1] # убираем угловые скобочки []
        
    else:
        # если кто-то зашел на страницу не выбрав расходники
        return HttpResponseRedirect(reverse('empty'))        

    if request.method == 'POST':
        
        try:
            firmid = int(request.POST['firm'])
            if firmid == 0:
                raise ValueError
        except ValueError:
            messages.error(request, 'Вы выбрали некорректную фирму')
            return render(request, 'index/transfer_to_firm.html', {'checked_cartr': checked_cartr, 
                                                                    'firms' : firms, 
                                                                })            
        else:
            
            select_firm = FirmTonerRefill.objects.get(pk=firmid) 
            for inx in tmp:
                m1 = CartridgeItem.objects.get(pk=inx)
                m1.cart_status = 4 # находится на заправке
                m1.filled_firm = select_firm
                m1.departament = None
                m1.save(update_fields=['filled_firm', 'cart_status', 'departament'])
        return HttpResponseRedirect(reverse('empty'))
    return render(request, 'index/transfer_to_firm.html', {'checked_cartr': checked_cartr, 
                                                            'firms' : firms, 
                                                            })


@login_required
def from_firm_to_stock(request):
    """Возврашаем заправленные расходники обратно на базу.
    """
    checked_cartr = request.GET.get('select', '')
    tmp = ''
    if checked_cartr:
        checked_cartr = checked_cartr.split('s')
        checked_cartr = [int(i) for i in checked_cartr]
        tmp = checked_cartr
        checked_cartr = str(checked_cartr)
        checked_cartr = checked_cartr[1:-1]
        
    else:
        # если кто-то зашел на страницу не выбрав расходники
        return HttpResponseRedirect(reverse('at_work'))        

    if request.method == 'POST':
        for inx in tmp:
            m1 = CartridgeItem.objects.get(pk=inx)
            m1.filled_firm = None
            m1.cart_status = 1
            m1.departament = request.user.departament
            m1.cart_number_refills = int(m1.cart_number_refills) + 1
            m1.save(update_fields=['filled_firm', 'cart_status', 'cart_number_refills', 'departament'])
        return HttpResponseRedirect(reverse('at_work'))
    return render(request, 'index/from_firm_to_stock.html', {'checked_cartr': checked_cartr })

def bad_browser(request):
    """Сообщение о необходимости обновить браузер.
    """
    return render(request, 'index/bad_browser.html')

def edit_cartridge_comment(request):
    """Добавляем комментарий к картриджу.
    """
    item_id = request.GET.get('id', '')
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
            cartridge_object.save(update_fields=['comment'])
            return HttpResponseRedirect(reverse('stock'))
    else:
        comment = cartridge_object.comment
        form = EditCommentForm(initial = {'comment': comment})
    return render(request, 'index/edit_cartridge_comment.html', {'form': form})
