# -*- coding:utf-8 -*-

import datetime
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.db.models import Q
from index.helpers import check_ajax_auth
from index.models import CartridgeItem, OrganizationUnits
from events.models import Events


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
            root_ou   = request.user.departament
            des       = root_ou.get_descendants()
        except:
            des = ''

        try:
            OrganizationUnits.objects.get(pk=org)
        except OrganizationUnits.DoesNotExist:
            result['error'] = 'Organization unit not found.'
        else:
            list_cart = CartridgeItem.objects.filter(Q(departament__in=des) | Q(departament=root_ou))
            list_cart = list_cart.filter(cart_number_refills__gte=cont).order_by('-cart_number_refills')
            html = render_to_string('reports/amortizing_ajax.html', context={'list_cart': list_cart})
            result['html'] = html
    return JsonResponse(result, safe=False)


@check_ajax_auth
def ajax_reports_users(request):
    """
    """
    from common.helpers import del_leding_zero
    import operator
    
    if request.method != 'POST':
        return HttpResponse('<h1>' + _('Only use POST requests!') + '</h1>')

    context = dict()
    prepare_list = request.POST.get('start_date', '')
    
    if not prepare_list:
        context['error'] = '1'
        context['text']  = _('Start date required field.')
        return JsonResponse(context)

    prepare_list = prepare_list.split(r'/')
    if len(prepare_list) == 3:
        # если пользователь не смухлевал, то кол-во элементов = 3
        date_value  = prepare_list[0]
        date_value  = del_leding_zero(date_value)
        month_value = prepare_list[1]
        month_value = del_leding_zero(month_value)
        year_value  = prepare_list[2]
        gte_date    = datetime.datetime(int(year_value), int(month_value), int(date_value))
    else:
        context['error'] = '1'
        context['text']  = _('Error in date data.')
        return JsonResponse(context)
    org = request.POST.get('org', '')
    try:
        org = int(org)
    except ValueError:
        org = 0
    try:
        root_ou  = OrganizationUnits.objects.get(pk=org)
    except OrganizationUnits.DoesNotExist:
        context['error'] = '1'
        context['text']  = _('Organization unit not found.')
        return JsonResponse(context)
    
    family = root_ou.get_descendants(include_self=False)
    result = dict()
    for child in family:
        m1  = Events.objects.all()
        m1  = m1.filter(event_org=child)
        m1  = m1.filter(event_type='TR')
        m1  = m1.filter(date_time__gte=gte_date)
        m1  = m1.count()
        result[str(child)] = m1

    result = sorted(result.items(), key=operator.itemgetter(1), reverse=True)
    context['text'] = render_to_string('reports/users_ajax.html', context={'result': result})
    context['error'] = '0'
    return JsonResponse(context)
