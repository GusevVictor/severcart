# -*- coding:utf-8 -*-

import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.db.models import Q
from .models  import Events
from index.models import CartridgeItem
from .helpers import events_decoder, date_to_str
from .forms   import DateForm


@login_required
def show_events(request):
    """Список всех событий для всего организационного подразделения.
    """
    context = {}
    MAX_EVENT_LIST = settings.MAX_EVENT_LIST
    try:
        dept_id = request.user.departament.pk
    except AttributeError:
        dept_id = 0
    list_events = Events.objects.filter(departament=dept_id).order_by('-pk')

    request.session['start_date'] = ''
    request.session['end_date'] = ''

    if request.method == 'POST':
        # попадаем в эту ветку если пользователь нажал на кнопку Показать
        date_form = DateForm(request.POST)
        if date_form.is_valid():
            data_in_post = date_form.cleaned_data
            # получаем данные для инициализации начальными значаниями заполненной формы
            start_date = date_to_str(data_in_post.get('start_date', ''))
            end_date   = date_to_str(data_in_post.get('end_date', ''))
            date_form = DateForm(initial={'start_date': start_date, 'end_date': end_date})
            # 
            start_date = data_in_post.get('start_date', '')
            end_date   = data_in_post.get('end_date', '')
            # сохраняем переданные даты в сессионном словаре, потом будем читать его значения из /events/api/ 
            request.session['start_date'] = start_date
            request.session['end_date']   = end_date
            # приводим словари, содержащие компоненты дат к объекту datetime
            if start_date:
                st_year  = int(start_date.get('year_value'))
                st_month = int(start_date.get('month_value'))
                st_date  = int(start_date.get('date_value'))
                
                start_date = datetime.datetime(st_year, st_month, st_date)
            if end_date:
                en_year  = int(end_date.get('year_value'))
                en_month = int(end_date.get('month_value'))
                en_date  = int(end_date.get('date_value'))

                end_date   = datetime.datetime(en_year, en_month, en_date)

            if start_date and not(end_date):
                list_events = list_events.filter(date_time__gte=start_date)

            elif not(start_date) and not(end_date):
                # выбираем все объекты если пользователь оставил поля ввода пустыми
                pass

            elif end_date and not(start_date):
                list_events = list_events.filter(date_time__lte=end_date)

            elif start_date == end_date :
                print('s = e')
                list_events = list_events.filter(date_time__year=end_date.year, 
                                           date_time__month=end_date.month, 
                                           date_time__day=end_date.day 
                                           )

            elif start_date and end_date:
                print('4', start_date, end_date)
                # вторая дата не попадает в диапазон, поэтому приболяем к ней 1 день
                end_date = end_date + datetime.timedelta(days=1)
                list_events = list_events.filter(Q(date_time__lte=end_date) & Q(date_time__gte=start_date))

            
            p = Paginator(list_events, MAX_EVENT_LIST)
            context['count_events'] = int(list_events.count())
            context['next_page'] = 2
            context['max_count_events'] = MAX_EVENT_LIST
            context['list_events'] = events_decoder(p.page(1), simple=False)
            context['form'] = date_form
            return render(request, 'events/show_events.html', context)

    # обычный get запрос
    date_form = DateForm()
    context['count_events'] = int(Events.objects.all().count())
    
    p = Paginator(list_events, MAX_EVENT_LIST)
    context['next_page'] = 2
    context['max_count_events'] = MAX_EVENT_LIST
    context['list_events'] = events_decoder(p.page(1), simple=False)
    context['form'] = date_form
    return render(request, 'events/show_events.html', context)    

@login_required
def view_cartridge_events(request):
    """Просмотр событий происходящих с данным картриджем.
    """
    cart_id = request.GET.get('id', '')
    try:
        cart_id = int(cart_id)
    except ValueError:
        raise Http404
    
    try:
        dept_id = request.user.departament.pk
    except AttributeError:
        dept_id = 0

    context = {}
    list_events = Events.objects.filter(cart_index=cart_id).filter(departament=dept_id).order_by('pk')
    try:
        frdly_es = events_decoder(list_events)
        context['frdly_es']     = frdly_es
        context['cart_number']  = list_events[0].cart_number
        context['cart_type']    = list_events[0].cart_type
    except IndexError:
        context['frdly_es']     = []
        context['cart_number']  = ''
        context['cart_type']    = 'Не найдено'
    return render(request, 'events/view_cartridge_events.html', context)
