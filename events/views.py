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

+14.05.2016 № 35 передан на заправку в фирму "Континент" пользователем вася
+14.05.2016 № 35 Возвращен с заправки в фирме "континент" васей
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
            text_com = 'Добавлен картридж № %s пользователем %s.' % (
                                                                                entry.cart_number,
                                                                                entry.event_user )
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'TR':
            entry_obj = {}
            data_env = entry.date_time
            text_com = '№ %s передан %s пользователем %s.' % (
                                                                        entry.cart_number,
                                                                        entry.event_org,
                                                                        entry.event_user )
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'TF':
            entry_obj = {}
            data_env = entry.date_time
            text_com = '№ %s передан на заправку "%s" пользователем %s.' % (
                                                                        entry.cart_number,
                                                                        entry.event_firm,
                                                                        entry.event_user )
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'RS':
            entry_obj = {}
            data_env = entry.date_time
            text_com = '№ %s возвращён с заправки в фирме "%s" пользователем %s.' % (
                                                                        entry.cart_number,
                                                                        entry.event_firm,
                                                                        entry.event_user )
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'TB':
            entry_obj = {}
            data_env = entry.date_time
            text_com = '№ %s перемещён в корзину пользователем %s.' % (
                                                                        entry.cart_number,
                                                                        entry.event_user )
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'DC':
            entry_obj = {}
            data_env = entry.date_time
            text_com = '№ %s списан пользователем %s.' % (
                                                                        entry.cart_number,
                                                                        entry.event_user )
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'TS':
            entry_obj = {}
            data_env = entry.date_time
            text_com = '№ %s возвращен от %s пользователем %s.' % (
                                                                        entry.cart_number,
                                                                        entry.event_org,
                                                                        entry.event_user )
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)
    
    context['frdly_es'] = frdly_es
    context['cart_id']  = cart_id
    context['cart_type'] = entry.cart_type
    return render(request, 'events/view_cartridge_events.html', context)