# -*- coding:utf-8 -*-

import json
from django.http import JsonResponse
from django.template.loader import render_to_string
#from django.utils.safestring import mark_safe
from index.helpers import check_ajax_auth
from index.models import CartridgeItem, OrganizationUnits


@check_ajax_auth
def ajax_report(request):
    """
    """
    result = {}
    action_type = request.POST.getlist('type')[0]
    if action_type == 'amortizing':
        org  = request.POST.getlist('org')[0]
        cont = request.POST.getlist('cont')[0]
        
        try:
            org = int(org)
        except ValueError:
            org = 0

        try:
            cont = int(cont)
        except ValueError:
            cont = 1

        try:
            departament = OrganizationUnits.objects.get(pk=org)
        except OrganizationUnits.DoesNotExist:
            result['error'] = 'Organization unit not found.'
        else:
            list_cart = CartridgeItem.objects.filter(departament=departament)
            list_cart = list_cart.filter(cart_number_refills__gte=cont).order_by('cart_number')
            html = render_to_string('reports/amortizing_ajax.html', context={'list_cart': list_cart})
            result['html'] = html

    return JsonResponse(result, safe=False)
