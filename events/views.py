# -*- coding:utf-8 -*-

import datetime
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from .models  import Events
from .helpers import events_decoder
from .forms   import DateForm

def date_to_str(date_dict):
    """Преобразует словарь содержащий компоненты дат в строку.
    """
    if isinstance(date_dict, dict):
        day   = date_dict.get('date_value', '')
        month = date_dict.get('month_value', '')
        year  = date_dict.get('year_value', '')
    else:
        return ''
    # добавляем лидирующий ноль
    day   = '0' + str(day) if day < 10 else str(day)
    month = '0' + str(month) if month < 10 else str(month)
    year  = str(year)
    return '/'.join([ day, month, year ])

def show_events(request):
    """Список всех событий для всего организационного подразделения.
    """
    context = {}
    MAX_EVENT_LIST = settings.MAX_EVENT_LIST
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
            # приводим словари, содержащие компоненты дат к объекту datetime
            if start_date:
                start_date = datetime.datetime(start_date.get('year_value'), start_date.get('month_value'), start_date.get('date_value'))
            if end_date:
                end_date   = datetime.datetime(end_date.get('year_value'), end_date.get('month_value'), end_date.get('date_value'))
            
            if start_date and not(end_date):
                m1 = Events.objects.filter(date_time__gte=start_date)

            elif not(start_date) and not(end_date):
                # выбираем все объекты если пользователь оставил поля ввода пустыми
                m1 = Events.objects.all()

            elif end_date and not(start_date):
                m1 = Events.objects.filter(date_time__lte=end_date)

            elif start_date == end_date :
                m1 = Events.objects.filter(date_time__year=end_date.year, 
                                           date_time__month=end_date.month, 
                                           date_time__day=end_date.day 
                                           )

            elif start_date and end_date:
                # вторая дата не попадает в диапазон, поэтому приболяем к ней 1 день
                end_date = end_date + datetime.timedelta(days=1)
                m1 = Events.objects.filter(Q(date_time__lte=end_date) & Q(date_time__gte=start_date))

            m1 = m1.order_by('-pk')
            context['count_events'] = int(m1.count())
            m1 = m1[:MAX_EVENT_LIST]
            context['max_count_events'] = MAX_EVENT_LIST
            context['list_events'] = events_decoder(m1, simple=False)
            context['form'] = date_form
            return render(request, 'events/show_events.html', context)

    # обычный get запрос
    date_form = DateForm()
    context['count_events'] = int(Events.objects.all().count())
    dept_id = request.user.departament.pk
    list_events = Events.objects.filter(departament=dept_id).order_by('-pk')[:MAX_EVENT_LIST]
    context['max_count_events'] = MAX_EVENT_LIST
    context['list_events'] = events_decoder(list_events, simple=False)
    context['form'] = date_form
    return render(request, 'events/show_events.html', context)    


def view_cartridge_events(request):
    """Просмотр событий происходящих с данным картриджем.
    """
    cart_id = request.GET.get('id', '')
    try:
        cart_id = int(cart_id)
    except ValueError:
        raise Http404
    es = Events.objects.filter(cart_number=cart_id).order_by('pk')
    context = {}
    frdly_es = events_decoder(es)
    context['frdly_es'] = frdly_es
    context['cart_id']  = cart_id
    context['cart_type'] = es[0].cart_type
    return render(request, 'events/view_cartridge_events.html', context)
