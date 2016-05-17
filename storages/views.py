from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.utils.translation import ugettext_lazy as _
from common.cbv import GridListView
from storages.models import Storages
from storages.forms import AddStorage

class ViewStorages(GridListView):
    """Вывод списка складских помещений организации.
    """
    @method_decorator(login_required)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(ViewStorages, self).dispatch(*args, **kwargs)

    def get(self, request, **kwargs):
        all_stor = Storages.objects.filter(departament=request.user.departament).order_by('pk')
        page_size = self.items_per_page()
        self.context['page_size'] = page_size
        self.context['storages'] = self.pagination(all_stor, page_size)
        return render(request, 'storages/list.html', self.context)


@login_required
@never_cache
def add_s(request):
    """Добавление нового складского помещения.
    """
    context = dict()
    if request.method == 'POST':
        form =AddStorage(request.POST)
        if form.is_valid():
            try:
                m1 = request.user.departament.pk
            except AttributeError:
                # если пользователь не ассоциирован с организацией,
                # то сообщаем об ошибке
                messages.error(request, _('User not assosiate with organization unit!<br/>Error code: 101.'))
                context['form'] = form
                return render(request, 'storages/add_s.html', context);

            data        = form.cleaned_data
            title       = data.get('title')
            address     = data.get('address')
            description = data.get('description') 
            m1 = Storages(
                        title       = title,
                        address     = address,
                        departament = request.user.departament,
                        description = description,
                        default     = False
                        )
            m1.save()
            messages.success(request, _('Starage "%(starage_name)s" success added.') % {'starage_name': title})
            context['form'] = form
        else:
            context['form'] = form
            messages.error(request, _('Starage not added.'))
    else:
        form = AddStorage()
        context['form'] = form     
    return render(request, 'storages/add_s.html', context);



@login_required
@never_cache
def edit_s(request):
    """Редактирование информации о складском помещении.
    """
    context = dict()
    select = request.GET.get('select', 0);
    try:
        select = int(select)
    except ValueError:
        select = 0
    try:
        m1 = Storages.objects.get(pk=select)
    except Storages.DoesNotExist:
        messages.error(request, _('Storage by id not found.'))
        m1 = False
    if request.method == 'POST':
        form =AddStorage(request.POST)
        if form.is_valid():
            data           = form.cleaned_data
            title          = data.get('title')
            address        = data.get('address')
            description    = data.get('description') 
            m1.title       = title
            m1.address     = address
            m1.description = description
            m1.save()
            messages.success(request, _('Starage "%(starage_name)s" success edited.') % {'starage_name': title})
            context['form'] = form
        else:
            context['form'] = form
            messages.error(request, _('Starage not edited.'))
    else:
        if m1:
            form =AddStorage(initial={
                             'title': m1.title, 
                             'address': m1.address,
                             'description': m1.description})
            context['form'] = form
    return render(request, 'storages/edit_s.html', context);
