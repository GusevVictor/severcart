# -*- coding:utf-8 -*-

import json, pytz
import datetime
from django.http import JsonResponse
from django.template import Template, Context
from django.http import Http404
from events.models import Events
from django.conf import settings
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from events.helpers import events_decoder
from common.helpers import is_admin
from index.helpers import check_ajax_auth
from events.forms   import DateForm
from service.helpers import SevercartConfigs

import logging
logger = logging.getLogger(__name__)

@check_ajax_auth
@is_admin
def show_event_page(request):
    """Передача списка событий исходя из номера пагинации.
    """
    tmp_dict = dict()
    if not(request.user.is_authenticated()):
        # если пользователь не аутентифицирован, то ничего не возвращаем
        jsonr = json.dumps({ 'authenticated': False })
        return JsonResponse(jsonr, safe=False)
    
    MAX_EVENT_LIST = settings.MAX_EVENT_LIST
    next_page = request.POST.get('next_page', '')
    try:
        next_page = int(next_page)
    except ValueError:
        next_page = 1

    try:
        dept_id = request.user.departament.pk
    except AttributeError:
        dept_id = 0
        
    list_events = Events.objects.filter(departament=dept_id).order_by('-pk')
    # возвращаем данные из сессионного словаря
    start_date  = request.session['start_date']
    end_date    = request.session['end_date']

    tmp_dict['has_next'] = 0
    conf = SevercartConfigs()
    if start_date:
        st_year  = int(start_date.get('year_value'))
        st_month = int(start_date.get('month_value'))
        st_date  = int(start_date.get('date_value'))
        
        start_date = datetime.datetime(year=st_year, 
                                        month=st_month, 
                                        day=st_date, 
                                        hour=0, 
                                        minute=0, 
                                        second=0, microsecond=0,
                                        tzinfo=pytz.timezone(conf.time_zone))        
    if end_date:
        en_year  = int(end_date.get('year_value'))
        en_month = int(end_date.get('month_value'))
        en_date  = int(end_date.get('date_value'))

        end_date = datetime.datetime(year=en_year, 
                                month=en_month, 
                                day=en_date, 
                                hour=0, 
                                minute=0, 
                                second=0, microsecond=0,
                                tzinfo=pytz.timezone(conf.time_zone))
        

    if start_date and not(end_date):
        list_events = list_events.filter(date_time__gte=start_date)

    elif not(start_date) and not(end_date):
        # выбираем все объекты если пользователь оставил поля ввода пустыми
        pass

    elif end_date and not(start_date):
        list_events = list_events.filter(date_time__lte=end_date)

    elif start_date == end_date :
        list_events = list_events.filter(date_time__year=end_date.year, 
                                   date_time__month=end_date.month, 
                                   date_time__day=end_date.day 
                                   )

    elif start_date and end_date:
        # вторая дата не попадает в диапазон, поэтому приболяем к ней 1 день
        end_date = end_date + datetime.timedelta(days=1)
        list_events = list_events.filter(Q(date_time__lte=end_date) & Q(date_time__gte=start_date))

    p = Paginator(list_events, MAX_EVENT_LIST)
    try:
        content = p.page(next_page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        content = p.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        #content = paginator.page(paginator.num_pages)
        tmp_dict['stop_pagination'] = '1'
        return JsonResponse(tmp_dict, safe=False)

    next_page = next_page + 1
    list_events = events_decoder(content, simple=False)
    html_content = ''
    for event_line in list_events:
        c = Context(dict(date_env = event_line.get('data_env','')))
        date_env = Template('{{ date_env|date:"d.m.Y G:i" }}').render(c)
        html_row = '<tr><td>%s</td><td>%s</td></tr>' % (date_env, event_line.get('text_com',''),)
        html_content += html_row
    tmp_dict['html_content'] = html_content
    tmp_dict['stop_pagination'] = '0'
    tmp_dict['next_page'] = next_page


    # если страница имеет следующую, то добавляем кнопку просмотреть ещё, иначе не добавляем
    if content.has_next():
        tmp_dict['has_next'] = 1

    return JsonResponse(tmp_dict, safe=False)


@check_ajax_auth
@is_admin
def date_filter(request):
    """Загрузка списка событий в соответствии с диапазонами.
    """
    ansver  = dict() # для ajax ответа на запрос
    context = dict() # для рендеринга списка событий
    ansver['has_next'] = 0
    try:
        dept_id = request.user.departament.pk
    except AttributeError:
        dept_id = 0

    time_zone_offset = request.POST.get('time_zone_offset', 0)
    try:
        time_zone_offset = int(time_zone_offset)
    except ValueError:
        time_zone_offset = 0

    next_page = request.POST.get('next_page', '')
    try:
        next_page = int(next_page)
    except ValueError:
        next_page = 1

    MAX_EVENT_LIST = settings.MAX_EVENT_LIST
    # попадаем в эту ветку если пользователь нажал на кнопку Показать
    date_form = DateForm(request.POST)
    list_events = Events.objects.filter(departament=dept_id).order_by('-pk')
    if date_form.is_valid():
        data_in_post = date_form.cleaned_data
        # получаем данные для инициализации начальными значаниями заполненной формы
        start_date = data_in_post.get('start_date', '')
        end_date   = data_in_post.get('end_date', '')
        # сохраняем переданные даты в сессионном словаре, потом будем читать его значения из /events/api/ 
        request.session['start_date'] = start_date
        request.session['end_date']   = end_date
        # приводим словари, содержащие компоненты дат к объекту datetime
        conf = SevercartConfigs()
        if start_date:
            st_year  = int(start_date.get('year_value'))
            st_month = int(start_date.get('month_value'))
            st_date  = int(start_date.get('date_value'))
            
            #start_date = datetime.datetime(st_year, st_month, st_date)
            start_date = datetime.datetime(year=st_year, 
                                month=st_month, 
                                day=st_date, 
                                hour=0, 
                                minute=0, 
                                second=0, microsecond=0,
                                tzinfo=pytz.timezone(conf.time_zone))
        if end_date:
            en_year  = int(end_date.get('year_value'))
            en_month = int(end_date.get('month_value'))
            en_date  = int(end_date.get('date_value'))

            #end_date   = datetime.datetime(en_year, en_month, en_date)
            end_date = datetime.datetime(year=en_year, 
                                month=en_month, 
                                day=en_date, 
                                hour=23, 
                                minute=59, 
                                second=59, microsecond=0,
                                tzinfo=pytz.timezone(conf.time_zone))

        if start_date and not(end_date):
            list_events = list_events.filter(date_time__gte=start_date)

        elif not(start_date) and not(end_date):
            # выбираем все объекты если пользователь оставил поля ввода пустыми
            pass

        elif end_date and not(start_date):
            list_events = list_events.filter(date_time__lte=end_date)

            """
            elif (start_date and end_date) :
                #list_events = list_events.filter(date_time__year=end_date.year, 
                #                           date_time__month=end_date.month, 
                #                           date_time__day=end_date.day,
                #                           date_time__hour=0,
                #                           date_time__minute=0,
                #                           date_time__second=0,
                #                           )
                list_events = list_events.filter(date_time__exact=start_date)
            """
        elif start_date and end_date:
            # вторая дата не попадает в диапазон, поэтому приболяем к ней 1 день
            end_date = end_date + datetime.timedelta(days=1)
            list_events = list_events.filter(Q(date_time__lte=end_date) & Q(date_time__gte=start_date))

        #p = Paginator(list_events, MAX_EVENT_LIST)
        p = Paginator(list_events, MAX_EVENT_LIST)
        try:
            content = p.page(next_page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            content = p.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            #content = paginator.page(paginator.num_pages)
            ansver['has_next'] = content.has_next()
            return JsonResponse(ansver, safe=False)

        #
        context['count_events'] = list_events.count()
        context['next_page'] = next_page + 1
        context['max_count_events'] = MAX_EVENT_LIST
        context['list_events'] = events_decoder(content, time_zone_offset, simple=False)
        html = render_to_string('events/show_all_events.html', context)
        ansver['html'] = html

        # если страница имеет следующую, то добавляем кнопку просмотреть ещё, иначе не добавляем
        if content.has_next():
            ansver['has_next'] = 1

        return JsonResponse(ansver)


@check_ajax_auth
def view_cart_events(request):
    """Просмотр событий для одного экземпляра картриджа.
    """
    ansver = dict()
    context = dict()
    cart_id = request.POST.get('cart_id', 0)
    try:
        cart_id = int(cart_id)
    except ValueError:
        raise Http404
    
    try:
        dept_id = request.user.departament.pk
    except AttributeError:
        dept_id = 0

    time_zone_offset = request.POST.get('time_zone_offset', 0)
    try:
        time_zone_offset = int(time_zone_offset)
    except ValueError:
        time_zone_offset = 0

    list_events = Events.objects.filter(cart_index=cart_id).filter(departament=dept_id).order_by('pk')
    try:
        frdly_es = events_decoder(list_events, time_zone_offset, simple=True)
        context['frdly_es']     = frdly_es
        context['cart_number']  = list_events[0].cart_number
        context['cart_type']    = list_events[0].cart_type
    except IndexError:
        context['frdly_es']     = []
        context['cart_number']  = ''
        context['cart_type']    = _('Not found')
    html = render_to_string('events/ajx_view_events_one_cartridge.html', context)
    ansver['html'] = html
    return JsonResponse(ansver)
