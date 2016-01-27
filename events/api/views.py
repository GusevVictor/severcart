# -*- coding:utf-8 -*-

import time
import json
import datetime
from django.http import JsonResponse, HttpResponse
from django.template import Template, Context
from events.models import Events
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from events.helpers import events_decoder, date_to_str
from index.helpers import check_ajax_auth

import logging
logger = logging.getLogger(__name__)

@check_ajax_auth
def show_event_page(request):
    """Передача списка событий исходя из номера пагинации.
    """
    tmp_dict = {}
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

    if start_date:
        start_date = datetime.datetime(start_date.get('year_value'), start_date.get('month_value'), start_date.get('date_value'))
    if end_date:
        end_date   = datetime.datetime(end_date.get('year_value'), end_date.get('month_value'), end_date.get('date_value'))

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


    list_events = events_decoder(content, simple=False)
    html_content = ''
    for event_line in list_events:
        c = Context(dict(date_env = event_line.get('data_env','')))
        date_env = Template('{{ date_env|date:"d.m.Y G:i" }}').render(c)
        html_row = '<tr><td>%s</td><td>%s</td></tr>' % (date_env, event_line.get('text_com',''),)
        html_content += html_row
    tmp_dict['html_content'] = html_content
    tmp_dict['stop_pagination'] = '0'
    return JsonResponse(tmp_dict, safe=False)
