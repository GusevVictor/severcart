from django.shortcuts import render_to_response, redirect
from django.shortcuts import render
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from .forms.authenticate import AuthenticationForm
from .forms.register import RegistrationForm


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
    """
    User registration view.
    """
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            return redirect(reverse('accounts:manage_users'))
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


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

    return redirect('/')