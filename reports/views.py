# -*- coding:utf-8 -*-

from django.shortcuts import render
import datetime
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.cache import never_cache
from common.helpers import BreadcrumbsPath
from .forms import NoUse, Amortizing, UsersCartridges
from index.models import CartridgeItem, OrganizationUnits

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
    if request.method == 'POST':
        form = Amortizing(request.POST)
        if form.is_valid():
            data_in_post = form.cleaned_data
            org  = data_in_post.get('org', '')
            cont = data_in_post.get('cont', '')
            list_cart = CartridgeItem.objects.filter(departament=org).filter(cart_number_refills__gte=cont)
            

            form = Amortizing(initial={ 'org': org, 'cont': cont })
            context['form'] = form
        else:
            # показываем форму, если произошли ошибки
            context['form'] = form

    # если GET метод ( или какой-либо другой) то создаём пустую форму
    else:
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
