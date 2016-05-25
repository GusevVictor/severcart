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
    try:
        cnum = int(cnum)
    except:
        context['cnum'] = cnum
        return render(request, 'search/error.html', context)

    try:
        cart_items = CartridgeItem.objects.filter(cart_number=cnum)
    except:
        return render(request, 'search/serp.html', context)
    
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
            link = reverse('index:toner_refill')
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
