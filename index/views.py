from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils import timezone
from index.forms.add_cartridge_type import AddCartridgeType
from index.forms.add_items import AddItems
from index.models import CartridgeType
from index.models import CartridgeItem
from .models import Category

# Create your views here.
def index(request):
    all_items = CartridgeItem.objects.all()
    return render(request, 'index/index.html', {'cartrjs': all_items})


def add_cartridge_type(request):

    if request.method == 'POST':
        form_obj = AddCartridgeType(request.POST)
        if form_obj.is_valid():
            # добавляем новый тип расходного материала
            form_obj.save()
            return HttpResponseRedirect(request.path)

    else:
        form_obj = AddCartridgeType()
        all_types = CartridgeType.objects.all()
    return render(request, 'index/add_type.html', {'form': form_obj, 'types': all_types})

def add_cartridge_item(request):

    if request.method == 'POST':
        form_obj = AddItems(request.POST)
        if form_obj.is_valid():
            # добавляем новый тип расходного материала
            all = form_obj.cleaned_data
            for i in range(int(all['cart_count'])):
                if all['cart_new']:
                    cart_uses_count = 0
                else:
                    cart_uses_count = 1
                m1 = CartridgeItem( cart_name = all['cart_name'],
                                    cart_type = all['cart_type'],
                                    cart_date_added = timezone.now(),
                                    cart_code = 0,
                                    cart_uses_count = cart_uses_count,
                                 #   cart_owner_id = 0,
                                    )
                m1.save()
            return HttpResponseRedirect(request.path)

    else:
        form_obj = AddItems()
        #all_types = CartridgeType.objects.all()
    return render(request, 'index/add_items.html', {'form': form_obj})

def tree_list(request):
    tree = Category()
    annotated_list = tree.get_annotated_list()
    return render(request, 'index/tree_list.html', {'annotated_list': annotated_list})