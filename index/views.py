# -*- coding:utf-8 -*-

import json
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.contrib import messages
from django.contrib.sessions.models import Session
from .forms.add_cartridge_name import AddCartridgeName
from .forms.add_items import AddItems
from .forms.add_city import CityF
from .forms.add_type import AddCartridgeType
from .forms.add_firm import FirmTonerRefillF
from .models import CartridgeType
from accounts.models import AnconUser
from django.contrib.auth.models import User
from .models import CartridgeItem
from .models import OrganizationUnits
from .models import City as CityM
from .models import FirmTonerRefill
from .models import Summary
from .helpers import recursiveChildren, check_ajax_auth
from .helpers import Dashboard

def dashboard(request):
    """Морда сайта. Отображает текущее состояние всего, что считаем.
    """
    context = {}
    context['full_on_stock'] = Summary.objects.get(pk=1).full_on_stock
    context['empty_on_stock'] = Summary.objects.get(pk=1).empty_on_stock
    context['uses'] = Summary.objects.get(pk=1).uses
    context['filled']  = Summary.objects.get(pk=1).filled

    return render(request, 'index/dashboard.html', context)

def stock(request):
    """

    """
    all_items = CartridgeItem.objects.filter(cart_owner__isnull=True).filter(cart_filled=True)
    paginator = Paginator(all_items, 8)

    page = request.GET.get('page')
    try:
        cartridjes = paginator.page(page)
    except PageNotAnInteger:
        cartridjes = paginator.page(1)
    except EmptyPage:
        cartridjes = paginator.page(paginator.num_pages)

    return render(request, 'index/stock.html', {'cartrjs': cartridjes})


def add_cartridge_name(request):
    if request.method == 'POST':
        form_obj = AddCartridgeName(request.POST)
        if form_obj.is_valid():
            # добавляем новый тип расходного материала
            form_obj.save()
            messages.success(request, 'Новое имя успешно добавлено.')
            return HttpResponseRedirect(request.path)

    else:
        form_obj = AddCartridgeName()
    return render(request, 'index/add_name.html', {'form': form_obj})


def add_cartridge_item(request):
    dash = Dashboard()
    if request.method == 'POST':
        form_obj = AddItems(request.POST)
        if form_obj.is_valid():
            # добавляем новый тип расходного материала
            data_in_post = form_obj.cleaned_data
            for i in range(int(data_in_post['cartCount'])):
                m1 = CartridgeItem(cart_itm_name=data_in_post['cartName'],
                                   cart_date_added=timezone.now(),
                                   cart_filled=True,
                                   cart_number_refills=0,
                                   )

                m1.save()
            dash.add_full_to_stock(num=int(data_in_post['cartCount']))
            messages.success(request, 'Расходники успешно добавлены.')
            return HttpResponseRedirect(request.path)

    else:
        form_obj = AddItems()
    return render(request, 'index/add_items.html', {'form': form_obj})


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



def add_type(request):
    """

    """
    if request.method == 'POST':
        form_obj = AddCartridgeType(request.POST)
        if form_obj.is_valid():
            data_in_post = form_obj.cleaned_data
            m1 = CartridgeType(cart_type=data_in_post['cart_type'])
            m1.save()
            messages.success(request, 'Новый тип успешно добавлен.')
            return HttpResponseRedirect(request.path)
    else:
        form_obj = AddCartridgeType()
    return render(request, 'index/add_type.html', {'form': form_obj})


def transfe_for_use(request):
    """

    """
    checked_cartr = request.GET.get('select', '')
    tmp = ''
    dash = Dashboard()
    if checked_cartr:
        checked_cartr = checked_cartr.split('s')
        checked_cartr = [int(i) for i in checked_cartr]
        tmp = checked_cartr
        checked_cartr = str(checked_cartr)
        checked_cartr = checked_cartr[1:-1]
        

    tree = Category()
    get = lambda node_id: Category.objects.get(pk=node_id)
    bulk = []
    for itm in tree.dump_bulk():
        bulk.extend(recursiveChildren(itm))

    if request.method == 'POST':
        data_in_post = request.POST
        parent_id = data_in_post['par_id']
        parent_id = int(parent_id)

        for inx in tmp:
            m1 = CartridgeItem.objects.get(pk=inx)
            m1.cart_owner = get(parent_id)
            m1.save(update_fields=['cart_owner'])
        
        dash.tr_cart_to_uses(num=len(tmp)) # срабатывает триггер перемещения едениц
        return HttpResponseRedirect(reverse('stock'))
    return render(request, 'index/transfe_for_use.html', {'checked_cartr': checked_cartr, 'bulk': bulk})


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
            m1.cart_owner = None
            m1.cart_filled = False
            m1.save(update_fields=['cart_owner', 'cart_filled'])

        return HttpResponseRedirect("/use/")
    return render(request, 'index/transfer_for_stock.html', {'checked_cartr': checked_cartr})


def use(request):
    """

    """
    all_items = CartridgeItem.objects.filter(cart_owner__isnull=False)
    return render(request, 'index/use.html', {'cartrjs': all_items})


def empty(request):
    """

    """
    items = CartridgeItem.objects.filter(filled_firm__isnull=True, 
                                        cart_owner__isnull=True,
                                        cart_filled=False,
                                        )
    return render(request, 'index/empty.html', {'cartrjs': items})


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
    paginator = Paginator(firms, 10)

    page = request.GET.get('page')
    try:
        show_firms = paginator.page(page)
    except PageNotAnInteger:
        show_firms = paginator.page(1)
    except EmptyPage:
        show_firms = paginator.page(paginator.num_pages)

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
                                                       'firms': show_firms,
                                                       'select': city_id,
                                                       'city_url': city_url_parametr
                                                       })


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


def manage_users(request):
    """

    """
    usr = AnconUser.objects.all()
    paginator = Paginator(usr, 8)

    page = request.GET.get('page')

    try:
        urs = paginator.page(page)
    except PageNotAnInteger:
        urs = paginator.page(1)
    except EmptyPage:
        urs = paginator.page(paginator.num_pages)

    print('urs=', urs)
    return render(request, 'index/manage_users.html', {'urs': urs})

def at_work(request):
    """Список картриджей находящихся на заправке.
    """
    items = CartridgeItem.objects.filter(filled_firm__isnull=False)
    
    paginator = Paginator(items, 8)
    page = request.GET.get('page')
    try:
        cartridjes = paginator.page(page)
    except PageNotAnInteger:
        cartridjes = paginator.page(1)
    except EmptyPage:
        cartridjes = paginator.page(paginator.num_pages)

    return render(request, 'index/at_work.html', {'cartrjs': items})



def transfer_to_firm(request):
    """Передача расходных материалов на заправку.
    """
    checked_cartr = request.GET.get('select', '')
    tmp = ''
    dash = Dashboard()
    firms = FirmTonerRefill.objects.all()
    if checked_cartr:
        checked_cartr = checked_cartr.split('s')
        checked_cartr = [int(i) for i in checked_cartr]
        checked_cartr = str(checked_cartr)
        checked_cartr = checked_cartr[1:-1]
        tmp = checked_cartr
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
                m1.filled_firm = select_firm
                m1.save()
            dash.tr_cart_to_uses(num=len(tmp))
        return HttpResponseRedirect(reverse('empty'))
    return render(request, 'index/transfer_to_firm.html', {'checked_cartr': checked_cartr, 
                                                            'firms' : firms, 
                                                            })

def from_firm_to_stock(request):
    """Возврашаем заправленные расходники обратно на базу.
    """
    checked_cartr = request.GET.get('select', '')
    tmp = ''
    dash = Dashboard()
    if checked_cartr:
        checked_cartr = checked_cartr.split('s')
        checked_cartr = [int(i) for i in checked_cartr]
        checked_cartr = str(checked_cartr)
        checked_cartr = checked_cartr[1:-1]
        tmp = checked_cartr
    else:
        # если кто-то зашел на страницу не выбрав расходники
        return HttpResponseRedirect(reverse('at_work'))        

    if request.method == 'POST':
        for inx in tmp:
            m1 = CartridgeItem.objects.get(pk=inx)
            m1.filled_firm = None
            m1.cart_filled = True
            m1.cart_number_refills = int(m1.cart_number_refills) + 1
            m1.save()
        dash.tr_cart_to_uses(num=len(tmp))
        return HttpResponseRedirect(reverse('at_work'))
    return render(request, 'index/from_firm_to_stock.html', {'checked_cartr': checked_cartr })

def bad_browser(request):
    """Сообщение о необходимости обновить браузер.
    """
    return render(request, 'index/bad_browser.html')