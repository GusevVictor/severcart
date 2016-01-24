# -*- coding:utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse, Http404
from .models import Events

def show_events(request):
    """Список событий для заданного картриджа.
    """
    return HttpResponse('<h1>Events it work!</h1>')

"""
номер события \ номер картриджа \ дата \ текст человекочитаемого события \
-----------------------------------------------------------
+12.04.2016 Добавлен картридж № 34 (12A) пользователем Вася  
+04.04.2016 № 45 передан в пользование "Каб. 290" пользователем Вася 

+18.02.2016 # 45 возвращен на склад пользователем Вася

+14.05.2016 № 35 передан на заправку в фирму "Континент" пользователем вася.
+14.05.2016 № 35 Возвращен с ремонта в фирме "континент" васей. 
                 Проводились следующие работы: заправка и очитска, замена фотовала.
+14.05.2016 № 35 перемещён в корзину васей 
+14.05.2016 № 35 утилизирован васей

"""

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
    frdly_es = []
    for entry in es:
        if entry.event_type == 'AD':
            entry_obj = {}
            data_env = entry.date_time
            text_com = 'Добавлен пользователем %s.' % (entry.event_user, )
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'TR':
            entry_obj = {}
            data_env = entry.date_time
            text_com = 'Передача в пользование %s пользователем %s.' % (
                                                                        entry.event_org,
                                                                        entry.event_user )
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'TF':
            entry_obj = {}
            data_env = entry.date_time
            text_com = 'Передача на заправку "%s" пользователем %s.' % (
                                                                        entry.event_firm,
                                                                        entry.event_user )
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'RS':
            entry_obj   = {}
            data_env    = entry.date_time
            entry.cart_action = '00000' if entry.cart_action == 0 else entry.cart_action
            action_num  = [ int(i) for i in str(entry.cart_action) ]
            action_text = ''
            action_text += 'заправка и очистка, ' if action_num[0] == 1 else ''
            action_text += 'замена фотовала, ' if action_num[1] == 1 else ''
            action_text += 'замена ракеля, ' if action_num[2] == 1 else ''
            action_text += 'замена чипа, ' if action_num[3] == 1 else ''
            action_text += 'замена магнитного вала, ' if action_num[4] == 1 else ''
            text_com    = 'Возврта с заправки в фирме "%s" пользователем %s.' % (
                                                                        entry.event_firm,
                                                                        entry.event_user )
            text_com += '<br/>Проводились следующие работы: '
            text_com += action_text 
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'TB':
            entry_obj = {}
            data_env = entry.date_time
            text_com = 'Перемещение в корзину пользователем %s.' % (entry.event_user, )
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'DC':
            entry_obj = {}
            data_env = entry.date_time
            text_com = 'Списание пользователем %s.' % (entry.event_user, )
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'TS':
            entry_obj = {}
            data_env = entry.date_time
            text_com = 'Возврат от %s пользователем %s.' % (
                                                                        entry.event_org,
                                                                        entry.event_user )
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)
    
    context['frdly_es'] = frdly_es
    context['cart_id']  = cart_id
    context['cart_type'] = entry.cart_type
    return render(request, 'events/view_cartridge_events.html', context)
