# -*- coding:utf-8 -*-

import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import Http404
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from common.helpers import BreadcrumbsPath
from .models  import Events
from .helpers import events_decoder, date_to_str
from events.forms   import DateForm
from common.helpers import is_admin


@login_required
@is_admin
@never_cache
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

    # сбрасываем все установленные установки дат в ноль
    request.session['start_date'] = ''
    request.session['end_date'] = ''

    # обычный get запрос
    date_form = DateForm()    
    context['form'] = date_form
    context['next_page'] = 2
    return render(request, 'events/show_events.html', context)    

@login_required
@never_cache
def view_cartridge_events(request):
    """Просмотр событий происходящих с данным картриджем.
    """
    context = dict()
    cart_id = request.GET.get('id', '')
    context['back'] = BreadcrumbsPath(request).before_page(request)
    return render(request, 'events/view_cartridge_events.html', context)
