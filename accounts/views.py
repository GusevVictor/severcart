from django.shortcuts import render_to_response, redirect
from django.shortcuts import render
from django.http import Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from .forms.authenticate import AuthenticationForm
from .forms.register import RegistrationForm
from accounts.models import AnconUser

import logging
logger = logging.getLogger('simp')

def login(request):
    """
    Log in view
    """
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                if user.is_active:
                    django_login(request, user)
                    return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def register(request):
    """Страница создания нового пользователя.
    """
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            return redirect(reverse('accounts:manage_users'))
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def edit_user(request):
    """Редактирование информации о пользователе.
    """
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            return redirect(reverse('accounts:manage_users'))
    else:
        uid = request.GET.get('id', '')
        try:
            uid = int(uid)
        except ValueError:
            uid = 0
        
        try:
            user_object = AnconUser.objects.get(pk=uid)
        except AnconUser.DoesNotExist:
            raise Http404
        
        username = user_object.username
        department = user_object.department
        fio = user_object.fio
        is_admin = user_object.is_admin
        form = RegistrationForm(initial = {'username': username,
                                           'department': department,
                                           'fio': fio,
                                           'is_admin': is_admin,
                                          })
    return render(request, 'accounts/edit_user.html', {'form': form})

def logout(request):
    """
    Log out view
    """
    django_logout(request)
    return redirect('/')


def edit(request):
    """

    """

    return redirect('/')


def delete(request):
    """
    """
    ar = request.POST.getlist('selected[]')
    ar = [int(i) for i in ar ]
    logger.debug(request.user.id)
    if request.user.id in ar:
        return HttpResponse('Ошибка! Пользователь %s не может удалить сам себя' % (request.user,))
    
    for ind in ar:
        usr = AnconUser.objects.get(pk=ind)
        usr.delete()
    return HttpResponse('User(s) deleted!')
