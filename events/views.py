# -*- coding:utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.cache import never_cache
from common.helpers import BreadcrumbsPath
from .models  import Events
from .helpers import date_to_str
from events.forms   import DateForm
from common.helpers import is_admin


@login_required
@is_admin
@never_cache
def show_events(request):
    """Список всех событий для всего организационного подразделения.
    """
    context = {}
    try:
        dept_id = request.user.departament.pk
    except AttributeError:
        dept_id = 0
    
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
    context['back'] = BreadcrumbsPath(request).before_page(request)
    return render(request, 'events/view_cartridge_events.html', context)
