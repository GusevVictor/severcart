# -*- coding:utf-8 -*-

import datetime, copy, json, csv, pytz
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.db import connection
from django.utils import formats
from django.views.decorators.http import require_POST
from collections import OrderedDict
from index.helpers import check_ajax_auth, str2int
from index.templatetags.filters import pretty_status
from index.models import CartridgeItem, OrganizationUnits
from common.helpers import rotator_files
from events.models import Events
from reports.forms import Firms, UsersCartridges, UseProducts
from reports.helpers import pretty_list
from docs.models import RefillingCart
from service.helpers import SevercartConfigs


@require_POST
@check_ajax_auth
def ajax_report(request):
    """Отчёт по амортизации РМ (количество перезаправок)
    """
    result = {}
    action_type = request.POST.getlist('type')[0]
    if action_type == 'amortizing':
        org  = request.POST.getlist('org')[0]
        cont = request.POST.getlist('cont')[0]
        org = str2int(org)
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

            # формируем выгрузку CSV файл
            csv_full_name, csv_file_name = rotator_files(request, file_type='csv')
            encoding = 'cp1251'
            with open(csv_full_name, 'w', newline='', encoding=encoding) as csvfile:
                fieldnames = ['number', 'name', 'date', 'amount', 'status']
                writer = csv.DictWriter(csvfile, fieldnames, delimiter=';')
                writer.writerow({'number': '', 'name': '', 'date': '', 'amount': '', 'status': ''})
                writer.writerow({'number': '', 'name': '', 'date': '', 'amount': '', 'status': ''})
                writer.writerow({'number': '', 'name': '', 'date': '', 'amount': '', 'status': ''})
                writer.writerow({'number': '', 'name': '', 'date': '', 'amount': '', 'status': ''})
                writer.writerow({'number': '', 'name': '', 'date': '', 'amount': '', 'status': ''})
                writer.writerow({'number': _('Number'), 'name': _('Name'), 'date': _('Date of last cases'), 'amount': _('Number refills'), 'status': _('Status')})
                for item in list_cart:
                    writer.writerow({'number': item.cart_number, 'name': item.cart_itm_name, 'date': formats.date_format(item.cart_date_change, 'd.m.Y'), 'amount': item.cart_number_refills, 'status': pretty_status(item.cart_status)})

            result['url'] = settings.STATIC_URL + 'csv/' + csv_file_name
    return JsonResponse(result, safe=False)


@require_POST
@check_ajax_auth
def ajax_reports_users(request):
    """
    """
    from common.helpers import del_leding_zero
    import operator
    context = dict()
    form = UsersCartridges(request.POST)
    if form.is_valid():
        data_in_post = form.cleaned_data
        start_date = data_in_post.get('start_date')
        end_date = data_in_post.get('end_date')
        org = data_in_post.get('org')
        unit = data_in_post.get('unit')
    else:
        context['error'] = '3'
        context['text']  = form.errors.as_json()
        return JsonResponse(context)
       
    if unit:
        root_ou = unit
        family = root_ou.get_descendants(include_self=True)

    else:
        root_ou = org
        family = root_ou.get_descendants(include_self=False)

    result = dict()
    if start_date and not(end_date):
        for child in family:
            m1  = Events.objects.all()
            m1  = m1.filter(event_org=child)
            m1  = m1.filter(event_type='TR')
            m1  = m1.filter(date_time__gte=start_date)
            m2 = m1
            m2 = m1.values('cart_type')
            m1  = m1.count()
            result[str(child)] = {'count': m1, 'details': pretty_list(list(m2))}
    elif start_date and end_date:
        for child in family:
            m1  = Events.objects.all()
            m1  = m1.filter(event_org=child)
            m1  = m1.filter(event_type='TR')
            m1  = m1.filter(date_time__gte=start_date)
            m1  = m1.filter(date_time__lte=end_date)
            m2 = m1
            m2 = m1.values('cart_type')
            m1  = m1.count()
            result[str(child)] = {'count': m1, 'details': pretty_list(list(m2))}
    else:
        result = 'Error'

    result = OrderedDict(sorted(result.items()))
    # сохраняем результаты работы скрипта в csv файле
    csv_full_name, csv_file_name = rotator_files(request, file_type='csv')
    encoding = 'cp1251'
    with open(csv_full_name, 'w', newline='', encoding=encoding) as csvfile:
        fieldnames = ['user', 'amount', 'details']
        writer = csv.DictWriter(csvfile, fieldnames, delimiter=';')
        writer.writerow({'user': '', 'amount': '', 'details': ''})
        writer.writerow({'user': '', 'amount': '', 'details': ''})
        writer.writerow({'user': '', 'amount': '', 'details': ''})
        writer.writerow({'user': _('Start range'), 'amount': start_date, 'details': ''})
        writer.writerow({'user': _('End range'), 'amount': end_date, 'details': ''})
        writer.writerow({'user': '', 'amount': '', 'details': ''})
        writer.writerow({'user': '', 'amount': '', 'details': ''})
        writer.writerow({'user': _('User'), 'amount': _('Items count'), 'details': _('Details')})
        for key, value in result.items():
            writer.writerow({'user': key, 'amount': value['count'], 'details': value['details']})

    context['text'] = render_to_string('reports/users_ajax.html', context={'result': result})
    context['url'] = settings.STATIC_URL + 'csv/' + csv_file_name
    context['error'] = '0'
    return JsonResponse(context)


@require_POST
@check_ajax_auth
def ajax_firm(request):
    """
    """
    context = dict()
    form = Firms(request.POST)
    context['error'] = '0'
    if form.is_valid():
        data_in_post = form.cleaned_data
        start_date = data_in_post.get('start_date')
        end_date = data_in_post.get('end_date')
        common_select = RefillingCart.objects.filter(doc_type=2).filter(departament=request.user.departament)
        if start_date and not(end_date):
            common_select = common_select.filter(date_created__gte=start_date)
        if not(start_date) and end_date: 
            common_select = common_select.filter(date_created__lte=end_date)
        if start_date and end_date:
            common_select = common_select.filter(Q(date_created__gte=start_date) & Q(date_created__lte=end_date))

        save_select = copy.copy(common_select)
        firms = common_select.values('firm').distinct().order_by('-pk')
        # убираем повторения, множества не годятся потому что каждая генерация меняет порядок
        unique_firms = list()
        for i in firms:
            if i['firm'] not in unique_firms:
                unique_firms.append(i['firm'])
        firms = None
        result = dict()
        # unique_firms = ['ГитХаб', 'Мегабит', 'Стиль']
        for f1 in unique_firms:
            if f1 == 'None':
                continue
            m1 = save_select.filter(firm=f1)
            for f2 in m1:
                # m1 = [<RefillingCart: 2016_65>, <RefillingCart: 2016_64>]
                act_data = f2.json_content
                act_data = json.loads(act_data)
                tmp_firm = result.get(f1, None)
                cl = len(act_data)
                last_count = cl if cl else 0
                last_money = f2.money if f2.money else 0                
                if tmp_firm:
                    bufer_count = result[f1]['count'] if result[f1]['count'] else 0
                    bufer_money = result[f1]['money'] if result[f1]['money'] else 0
                    result[f2.firm] = {'count': last_count + bufer_count, 'money': last_money + bufer_money}
                else:
                    result[f1] = {'count': last_count, 'money': last_money}

        # генерируем CSV документ для последующей работы
        csv_full_name, csv_file_name = rotator_files(request, file_type='csv')
        encoding = 'cp1251'
        with open(csv_full_name, 'w', newline='', encoding=encoding) as csvfile:
            fieldnames = ['name', 'amount', 'money']
            writer = csv.DictWriter(csvfile, fieldnames, delimiter=';')
            writer.writerow({'name': '', 'amount': '', 'money': ''})
            writer.writerow({'name': '', 'amount': '', 'money': ''})
            writer.writerow({'name': '', 'amount': '', 'money': ''})
            writer.writerow({'name': _('Start range'), 'amount': start_date, 'money': ''})
            writer.writerow({'name': _('End range'), 'amount': end_date, 'money': ''})
            writer.writerow({'name': '', 'amount': '', 'money': ''})
            writer.writerow({'name': '', 'amount': '', 'money': ''})
            writer.writerow({'name': _('Firm name'), 'amount': _('The number of serviced objects'), 'money': '%s, %s' % (_('The money paid'), _('Currency'))})
            for key, value in result.items():
                writer.writerow({'name': key, 'amount': value['count'], 'money': value['money']/100})

        context['error'] = '0'
        context['url'] = settings.STATIC_URL + 'csv/' + csv_file_name
        context['text'] = render_to_string('reports/worket_firms.html', context={'result': result})

    else:
        context['text'] = form.errors.as_text()
        context['error'] = '1'

    return JsonResponse(context)


@require_POST
@check_ajax_auth
def ajax_reports_brands(request):
    """Отчёт по потреблённым наименованиям
    """
    from common.helpers import del_leding_zero
    import operator
    context = dict()
    form = UseProducts(request.POST)
    if form.is_valid():
        data_in_post = form.cleaned_data
        start_date = data_in_post.get('start_date')
        end_date = data_in_post.get('end_date')
        org = data_in_post.get('org')
        unit = data_in_post.get('unit')
    else:
        context['error'] = '3'
        context['text']  = form.errors.as_json()
        return JsonResponse(context)
       
    if unit:
        child = unit
        root_ou = False
        #family = root_ou.get_descendants(include_self=True)
    else:
        root_ou = org
        root_ou = root_ou.pk
        child = False
        #family = root_ou.get_descendants(include_self=False)

    result = list()
    conf = SevercartConfigs()
    time_offset = datetime.datetime.now(pytz.timezone(conf.time_zone)).strftime('%z')
    start_date = start_date + time_offset
    if end_date:
        end_date = end_date + time_offset
    
    if child and start_date and not(end_date):
        # если определена дата начала анализа, дата окончания пропущена
        SQL_QUERY = """SELECT 
                            cart_type, COUNT(cart_type) as cart_count 
                        FROM 
                            events_events 
                        WHERE
                            event_type = 'TR' AND event_org = '%s' AND 
                            date_time >= '%s'
                        GROUP BY 
                            cart_type
                        ORDER BY cart_count DESC;
                    """ % (child, start_date,)
    if child and not(start_date) and end_date:               
        # если проеделена крайняя дата просмотра, а дата начала 
        # не определена
        SQL_QUERY = """SELECT 
                            cart_type, 
                            COUNT(cart_type) as cart_count
                        FROM 
                            events_events 
                        WHERE
                            event_type = 'TR' AND event_org = '%s' AND 
                        date_time <= '%s'
                        GROUP BY 
                            cart_type
                        ORDER BY cart_count DESC;
                    """ % (child, end_date,)

    if child and start_date and end_date:
        SQL_QUERY = """SELECT 
                            cart_type, COUNT(cart_type) as cart_count
                        FROM 
                            events_events
                        WHERE 
                            event_type = 'TR' AND event_org = '%s' AND 
                            date_time >= '%s' AND date_time <= '%s'
                        GROUP BY
                            cart_type
                        ORDER BY cart_count DESC;
                    """ % (child, start_date, end_date,)
    # ветка для SQL запросов если выбран депртамент, а орг. подразделение нет
    if root_ou and start_date and not(end_date):
        # если определена дата начала анализа, дата окончания пропущена
        SQL_QUERY = """SELECT 
                            cart_type, COUNT(cart_type) as cart_count 
                        FROM 
                            events_events 
                        WHERE
                            event_type = 'TR' AND departament = %s AND 
                            date_time >= '%s'
                        GROUP BY 
                            cart_type
                        ORDER BY cart_count DESC;
                    """ % (root_ou, start_date,)
    if root_ou and not(start_date) and end_date:               
        # если проеделена крайняя дата просмотра, а дата начала 
        # не определена
        SQL_QUERY = """SELECT 
                            cart_type, 
                            COUNT(cart_type) as cart_count
                        FROM 
                            events_events 
                        WHERE
                            event_type = 'TR' AND departament = %s AND 
                        date_time <= '%s'
                        GROUP BY 
                            cart_type
                        ORDER BY cart_count DESC;
                    """ % (root_ou, end_date,)

    if root_ou and start_date and end_date:
        SQL_QUERY = """SELECT 
                            cart_type, COUNT(cart_type) as cart_count
                        FROM 
                            events_events
                        WHERE 
                            event_type = 'TR' AND departament = %s AND 
                            date_time >= '%s' AND date_time <= '%s'
                        GROUP BY
                            cart_type
                        ORDER BY cart_count DESC;
                    """ % (root_ou, start_date, end_date,)


    #####
    cursor = connection.cursor()
    cursor.execute(SQL_QUERY)
    data = cursor.fetchall()
    result = data
    # сохраняем результаты работы скрипта в csv файле
    csv_full_name, csv_file_name = rotator_files(request, file_type='csv')
    encoding = 'cp1251'
    with open(csv_full_name, 'w', newline='', encoding=encoding) as csvfile:
        fieldnames = ['name', 'amount']
        writer = csv.DictWriter(csvfile, fieldnames, delimiter=';')
        writer.writerow({'name': '', 'amount': ''})
        writer.writerow({'name': '', 'amount': ''})
        writer.writerow({'name': '', 'amount': ''})
        writer.writerow({'name': _('Start range'), 'amount': start_date})
        writer.writerow({'name': _('End range'), 'amount': end_date})
        writer.writerow({'name': '', 'amount': ''})
        writer.writerow({'name': '', 'amount': ''})
        writer.writerow({'name': _('Name'), 'amount': _('Items count')})
        for item in result:
            writer.writerow({'name': item[0], 'amount': item[1]})

    context['text'] = render_to_string('reports/brands_ajax.html', context={'result': result})
    context['url'] = settings.STATIC_URL + 'csv/' + csv_file_name
    context['error'] = '0'
    return JsonResponse(context)
