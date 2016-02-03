from django.shortcuts import render
import datetime
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import NoUse
from index.models import CartridgeItem, OrganizationUnits

@login_required
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

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NoUse(initial={'org': dept_id })
        context['form'] = form

    return render(request, 'reports/main_summary.html', context)

@login_required
def amortizing(request):
    """
    """
    context = {}
    return render(request, 'reports/main_summary.html', context)

@login_required
def users(request):
    """
    """
    context = {}
    return render(request, 'reports/main_summary.html', context)
