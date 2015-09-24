from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from index.forms.add_cartridge_name import AddCartridgeName
from index.forms.add_items import AddItems
from .forms.add_type import AddCartridgeType
from .models import CartridgeType
from .models import CartridgeItem
from .models import Category
from .models import City
from .models import FirmTonerRefill
from .helpers import recursiveChildren

# Create your views here.
def index(request):

    #all_items = CartridgeItem.objects.filter(cart_filled=True)
    all_items = CartridgeItem.objects.filter(cart_owner__isnull=True).filter(cart_filled=True)
    paginator = Paginator(all_items, 8)

    page = request.GET.get('page')
    try:
        cartridjes = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        cartridjes = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
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
            all = form_obj.cleaned_data
            for i in range(int(all['cart_count'])):
                m1 = CartridgeItem(cart_itm_name=all['cart_name'],
                                   cart_date_added=timezone.now(),
                                   cart_code=0,
                                   cart_filled=True,
                )
                m1.save()
            return HttpResponseRedirect(request.path)

    else:
        form_obj = AddItems()
    return render(request, 'index/add_items.html', {'form': form_obj})


def tree_list(request):

    tree = Category()
    get = lambda node_id: Category.objects.get(pk=node_id)

    if request.method == 'POST':
        all = request.POST
        parent_id = all['par_id']
        parent_id = int(parent_id)
        unit_name = all['name']  # очень не безопасно!

        if parent_id:
            node = get(parent_id).add_child(name=unit_name)
        else:
            tree.add_root(name=unit_name)

    annotated_list = tree.get_annotated_list()

    bulk = []
    for itm in tree.dump_bulk():
        bulk.extend(recursiveChildren(itm))

    return render(request, 'index/tree_list.html', {'annotated_list': annotated_list, 'bulk' : bulk})


def add_type(request):
    """

    """
    if request.method == 'POST':
        form_obj = AddCartridgeType(request.POST)
        if form_obj.is_valid():
            all = form_obj.cleaned_data
            m1 = CartridgeType(cart_type=all['cart_type'])
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
        all = request.POST
        parent_id = all['par_id']
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

    city = request.GET.get('city', '')
    cities = City.objects.all()

    try:
        city = City.objects.get(city_name=city)
    except City.DoesNotExist:
        city = None


    if city:
        firms = FirmTonerRefill.objects.filter(firm_city=city)
    else:
        firms = FirmTonerRefill.objects.all()

    return render(request, 'index/toner_refill.html', {'cities': cities, 'firms': firms})
