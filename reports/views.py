from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import NoUse
from index.models import OrganizationUnits

@login_required
def main_summary(request):
    """
    """
    context = {}
    dept_id = request.user.departament.pk
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
