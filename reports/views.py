# -*- coding:utf-8 -*-

from django.shortcuts import render
import datetime
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.utils import timezone
from django.db import connection
from django.views.decorators.cache import never_cache
from common.helpers import BreadcrumbsPath
from reports.forms import NoUse, Amortizing, UsersCartridges, UseProducts, Firms
from index.models import CartridgeItem, OrganizationUnits


@login_required
@never_cache
def main_summary(request):
    """
    """
    context = {}
    try:
        dept_id = request.user.departament.pk
    except:
        dept_id = 0

    form = NoUse(initial={'org': dept_id })
    context['form'] = form

    return render(request, 'reports/main_summary.html', context)


@login_required
@never_cache
def amortizing(request):
    """Отчёт по амортизации. Выбрать списки картриджей с заданным количеством перезаправок.
    """
    context = {}
    try:
        dept_id = request.user.departament.pk
    except:
        dept_id = 0
    context['form'] = Amortizing(initial={'org': dept_id, 'cont': 1 })

    return render(request, 'reports/amortizing.html', context)


@login_required
@never_cache
def users(request):
    """
    """
    context = dict()
    form = UsersCartridges()
    form.fields['unit'].queryset = OrganizationUnits.objects.filter(pk=0)
    context['form'] = form
    return render(request, 'reports/users.html', context)


@login_required
@never_cache
def products(request):
    """Отчёт о используемых наименований РМ и их количестве за период.
    """
    context = dict()
    form = UseProducts()
    form.fields['unit'].queryset = OrganizationUnits.objects.filter(pk=0)
    context['form'] = form
    return render(request, 'reports/products.html', context)


@login_required
@never_cache
def spent_money(request):
    """Отчёт о потраченных суммах по заправке за период.
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
                                    SUM(money) as spent_money 
                                FROM 
                                    docs_refillingcart 
                                WHERE
                                    departament_id = %s AND 
                                    date_created >= '%s'
                                ORDER BY spent_money DESC;
                            """ % (org, start_date,)
            if not(start_date) and end_date:               
                # если проеделена крайняя дата просмотра, а дата начала 
                # не определена
                SQL_QUERY = """SELECT 
                                    SUM(money) as spent_money
                                FROM 
                                    docs_refillingcart 
                                WHERE
                                    departament_id = %s AND
                                    date_created <= '%s'
                                GROUP BY 
                                    cart_type
                                ORDER BY spent_money DESC;
                            """ % (org, end_date,)

            if start_date and end_date:
                SQL_QUERY = """SELECT 
                                    SUM(money) as spent_money
                                FROM 
                                    docs_refillingcart
                                WHERE 
                                    departament_id = %s AND 
                                    date_created >= '%s' AND date_created <= '%s'
                                ORDER BY spent_money DESC;
                            """ % (org, start_date, end_date,)                
            cursor = connection.cursor()
            cursor.execute(SQL_QUERY)
            context['all_items'] = cursor.fetchall()
        else:
            print('Form invalid')
        
    else:
        context['form'] = UseProducts(initial={'org': request.user.departament})
    return render(request, 'reports/spent_money.html', context)


@login_required
@never_cache
def firm(request):
    """Отчёт по заправщикам. Кто,сколько и за какие деньги заправил расходники.
    """
    context = dict()
    form = Firms()
    context['form'] = form
    return render(request, 'reports/firm.html', context)
