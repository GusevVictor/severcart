# -*- coding:utf-8 -*-

from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from index.models import CartridgeItem, STATUS


@login_required
@never_cache
def search(request):
    """Реализация простого механизма поиска картриджа по номеру.
    """
    cnum = request.GET.get('query', '')
    context = {}
    cnum = cnum.strip()
    
    cart_items = CartridgeItem.objects.filter(cart_number__icontains=cnum)
    if not cart_items:
        context['cart_items'] = []
        return render(request, 'search/serp.html', context)
    
    try:
        root_ou   = request.user.departament
        des       = root_ou.get_descendants(include_self=True)
    except:
        cart_items = []
    else:
        cart_items = cart_items.filter(departament__in=des)
    
    tmp_list = list()
    for elem in cart_items:
        # формируем человеко читаемый формат статуса картриджа на складе    
        for st in STATUS:
            if elem.cart_status == st[0]:
                cart_status = st[1]
                break

        link = ''
        if elem.cart_status == 1:
            link = reverse('index:stock')
        elif elem.cart_status == 2:
            link = reverse('index:use')
        elif elem.cart_status == 3:
            link = reverse('index:empty')
        elif elem.cart_status == 4:
            link = reverse('index:at_work', args=[elem.filled_firm.pk])
        elif elem.cart_status == 5:
            link = reverse('index:basket')
        else:
            link = reverse('index:basket')

        tmp_list.append({'cart_number': elem.cart_number,
                          'cart_itm_name': elem.cart_itm_name,
                          'departament': elem.departament,
                          'cart_status': cart_status,
                          'cart_date_added': elem.cart_date_added,
                          'link': link,
                          'comment': elem.comment,
                        })

    context['cart_items'] = tmp_list
    return render(request, 'search/serp.html', context)
