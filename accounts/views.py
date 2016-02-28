# -*- coding:utf-8 -*-

from django.shortcuts import render_to_response, redirect
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.template import RequestContext
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.contrib.auth.decorators import login_required
from common.helpers import BreadcrumbsPath
from .forms.authenticate import AuthenticationForm
from .forms.register import RegistrationForm
from .forms.edit import EditUserForm
from .forms.chpswd import ChangePassword
from accounts.models import AnconUser
from common.helpers import is_admin


import logging
logger = logging.getLogger('simp')


@login_required
@is_admin
def manage_users(request):
    """Вывод списка пользователей программы.
    """
    usr = AnconUser.objects.all()
    return render(request, 'accounts/manage_users.html', {'urs': usr })


def login(request):
    """Log in view
    """
    error = True
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            try:
                user = authenticate(username=request.POST['username'], password=request.POST['password'])
            except AnconUser.DoesNotExist:
                user = None
            if user is not None:
                if user.is_active:
                    django_login(request, user)
                    return redirect('/')
    else:
        error = False
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form, 'error': error, 'demo': settings.DEMO})


@login_required
@is_admin
def register(request):
    """Страница создания нового пользователя.
    """
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            if not settings.DEMO:
                # если активирован режим ДЕМО, то нового пользователя не создаём
                user = form.save()
            return redirect(reverse('auth:manage_users'))
        else:
            form = form
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
@is_admin
def edit_user(request):
    """Редактирование информации о пользователе.
    """
    if request.method == 'POST':
        form = EditUserForm(data=request.POST)

        if form.is_valid():
            if not settings.DEMO:
                # если активирован режим ДЕМО, то изменения параметров не производим
                user = form.save()
            return redirect(reverse('auth:manage_users'))
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
        try:
            departament = user_object.departament
        except AttributeError:
            departament = ''    
        
        try:
            fio = user_object.fio
        except AttributeError:
            fio = ''

        try:
            email = user_object.email
        except AttributeError:
            email = ''

        is_admin = user_object.is_admin
        form = EditUserForm(initial = {'user_id': uid,
                                        'username': username,
                                        'departament': departament,
                                        'fio': fio,
                                        'email': email,
                                        'is_admin': is_admin,
                                        })
    return render(request, 'accounts/edit_user.html', {'form': form})


def logout(request):
    """
    Log out view
    """
    django_logout(request)
    return redirect('/')


@login_required
@is_admin
def edit(request):
    """
    """
    return redirect('/')


@login_required
@is_admin
def delete(request):
    """
    """
    ar = request.POST.getlist('selected[]')
    ar = [int(i) for i in ar ]
    logger.debug(request.user.id)
    if request.user.id in ar:
        return HttpResponse(_('Error! User %(user_name)s can not remove himself') % {'user_name': request.user})
    
    for ind in ar:
        usr = AnconUser.objects.get(pk=ind)
        usr.delete()
    return HttpResponse(_('User(s) deleted!'))


@login_required
@is_admin
def change_password(request):
    """Смена пароля пользователя.
    """
    context = {}
    context['back'] = BreadcrumbsPath(request).before_page(request)
    uid = request.GET.get('id', '')
    try:
        uid = int(uid)
    except ValueError:
        uid = 0
    
    try:
        user_object = AnconUser.objects.get(pk=uid)
    except AnconUser.DoesNotExist:
        raise Http404

    context['username'] = user_object.username

    if request.method == 'POST':
        form = ChangePassword(request.POST)
        print('form=', form)
        if form.is_valid():
            data_in_post = form.cleaned_data
            passwd = data_in_post.get('password1')
            if not settings.DEMO:
                # если выбран режим демонстрации, то менять пароль не разрешаем.
                user_object.set_password(passwd)
                user_object.save()
            return HttpResponseRedirect(reverse('auth:manage_users'))
        else:
            context['form'] = form
    else:
        context['form'] = ChangePassword()
    return render(request, 'accounts/change_password.html', context)