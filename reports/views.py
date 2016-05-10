# -*- coding:utf-8 -*-

from django.shortcuts import render
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import connection
from django.views.decorators.cache import never_cache
from common.helpers import BreadcrumbsPath
from reports.forms import NoUse, Amortizing, UsersCartridges, UseProducts
from index.models import CartridgeItem


@login_required
@never_cache
def main_summary(request):
    """
    """
    context = {}
    dept_id = request.user.departament.pk
    if request.method == 'POST':
        form = NoUse(request.POST)
        if form.is_valid():
            data_in_post = form.cleaned_data
            org  = data_in_post.get('org', '')
            diap = data_in_post.get('diap', '')
            if (diap == 10) or (diap == 20):
                old_cart = CartridgeItem.objects.filter(departament=org)
                old_cart = old_cart.order_by('cart_date_change')[:diap]
                context['old_cart'] = old_cart
            elif diap == 0:
                cur_date = timezone.now()
                old_cart = CartridgeItem.objects.filter(departament=org)
                last_year = datetime.datetime(cur_date.year - 1, cur_date.month, cur_date.day)
                old_cart = old_cart.filter(cart_date_change__lte=last_year).order_by('cart_date_change')
                context['old_cart'] = old_cart
            else:
                pass

            form = NoUse(initial={ 'org': org, 'diap': diap })
            context['form'] = form
        else:
            # показываем форму, если произошли ошибки
            context['form'] = form

    # если GET метод ( или какой-либо другой) то создаём пустую форму
    else:
        form = NoUse(initial={'org': dept_id })
        context['form'] = form

    return render(request, 'reports/main_summary.html', context)

@login_required
@never_cache
def amortizing(request):
    """Отчёт по амортизации. Выбрать списки картриджей с заданным количеством перезаправок.
    """
    context = {}
    dept_id = request.user.departament.pk
    context['form'] = Amortizing(initial={'org': dept_id, 'cont': 1 })

    return render(request, 'reports/amortizing.html', context)

@login_required
@never_cache
def users(request):
    """
    """
    context = {}
    context['back'] = BreadcrumbsPath(request).before_page(request)
    if request.method == 'POST':
        pass
    else: 
        context['form'] = UsersCartridges(initial={'org': request.user.departament})
    return render(request, 'reports/users.html', context)

@login_required
@never_cache
def products(request):
    """Отчёт о используемых наименований РМ и их количестве за период.
    """
    context = dict()
    if request.method == 'POST':
        form = UseProducts(request.POST)
        context['form'] = form
        if form.is_valid():
            data_in_post = form.cleaned_data
            org          = data_in_post.get('org', '')
            start_date   = data_in_post.get('start_date', '')
            end_date     = data_in_post.get('end_date', '')
            
            #
            if start_date and not(end_date):
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
                            """ % (org, start_date,)
            if not(start_date) and end_date:               
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
                            """ % (org, end_date,)

            if start_date and end_date:
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
                            """ % (org, start_date, end_date,)                
            cursor = connection.cursor()
            cursor.execute(SQL_QUERY)
            context['all_items'] = cursor.fetchall()
            print('all_items = ', context['all_items'])
        else:
            print('Form invalid')
        
    else:
        context['form'] = UseProducts()
    return render(request, 'reports/products.html', context)
