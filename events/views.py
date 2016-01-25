# -*- coding:utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.conf import settings
from .models import Events
from .helpers import events_decoder


def show_events(request):
    """Список всех событий для всего организационного подразделения.
    """
    context = {}
    MAX_EVENT_LIST = settings.MAX_EVENT_LIST
    dept_id = request.user.departament.pk
    list_events = Events.objects.filter(departament=dept_id).order_by('-pk')[:MAX_EVENT_LIST]
    print('list_events=', len(list_events))
    context['list_events'] = events_decoder(list_events, simple=False)
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
