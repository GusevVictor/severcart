# -*- coding:utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import Http404
from .forms.add_cartridge_name import AddCartridgeName
from .forms.add_items import AddItems
from .forms.add_city import CityF
from .forms.add_type import AddCartridgeType
from .forms.add_firm import FirmTonerRefillF
from .forms.add_user import AddUser
from .models import CartridgeType
from accounts.models import AnconUser
from django.contrib.auth.models import User
from .models import CartridgeItem
from .models import Category
from .models import City as CityM
from .models import FirmTonerRefill
from .helpers import recursiveChildren


def index(request):

    all_items = CartridgeItem.objects.filter(cart_owner__isnull=True).filter(cart_filled=True)
    paginator = Paginator(all_items, 8)

    page = request.GET.get('page')
    try:
        cartridjes = paginator.page(page)
    except PageNotAnInteger:
        cartridjes = paginator.page(1)
    except EmptyPage:
        cartridjes = paginator.page(paginator.num_pages)

    return render(request, 'index/index.html', {'cartrjs': cartridjes})


def add_cartridge_name(request):
    if request.method == 'POST':
        form_obj = AddCartridgeName(request.POST)
        if form_obj.is_valid():
            # добавляем новый тип расходного материала
            form_obj.save()
            return HttpResponseRedirect(request.path)

    else:
        form_obj = AddCartridgeName()
    return render(request, 'index/add_name.html', {'form': form_obj})


def add_cartridge_item(request):
    if request.method == 'POST':
        form_obj = AddItems(request.POST)
        if form_obj.is_valid():
            # добавляем новый тип расходного материала
            data_in_post = form_obj.cleaned_data
            for i in range(int(data_in_post['cart_count'])):
                m1 = CartridgeItem(cart_itm_name=data_in_post['cart_name'],
                                   cart_date_added=timezone.now(),
                                   cart_filled=True,)
                m1.save()
            return HttpResponseRedirect(request.path)

    else:
        form_obj = AddItems()
    return render(request, 'index/add_items.html', {'form': form_obj})


def tree_list(request):

    tree = Category()
    get = lambda node_id: Category.objects.get(pk=node_id)

    if request.method == 'POST':
        data_in_post = request.POST
        parent_id = data_in_post['par_id']
        parent_id = int(parent_id)
        unit_name = data_in_post['name']  # очень не безопасно!

        if parent_id:
            node = get(parent_id).add_child(name=unit_name)
        else:
            tree.add_root(name=unit_name)

    annotated_list = tree.get_annotated_list()

    bulk = []
    for itm in tree.dump_bulk():
        bulk.extend(recursiveChildren(itm))

    return render(request, 'index/tree_list.html', {'annotated_list': annotated_list, 'bulk': bulk})


def add_type(request):
    """

    """
    if request.method == 'POST':
        form_obj = AddCartridgeType(request.POST)
        if form_obj.is_valid():
            data_in_post = form_obj.cleaned_data
            m1 = CartridgeType(cart_type=data_in_post['cart_type'])
            m1.save()
            return HttpResponseRedirect(request.path)
    else:
        form_obj = AddCartridgeType()
    return render(request, 'index/add_type.html', {'form': form_obj})


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

    tree = Category()
    get = lambda node_id: Category.objects.get(pk=node_id)
    bulk = []
    for itm in tree.dump_bulk():
        bulk.extend(recursiveChildren(itm))

    if request.method == 'POST':
        data_in_post = request.POST
        parent_id = data_in_post['par_id']
        parent_id = int(parent_id)
        #print('parent_id=', get(parent_id))

        for inx in tmp:
            m1 = CartridgeItem.objects.get(pk=inx)
            m1.cart_owner = get(parent_id)
            m1.save(update_fields=['cart_owner'])

        return HttpResponseRedirect("/")
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
    items = CartridgeItem.objects.filter(cart_owner__isnull=True, cart_filled=False)
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
                                                       'city_url': city_url_parametr})


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

