# -*- coding:utf-8 -*-

import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.views.decorators.cache import never_cache
from django.utils.translation import ugettext as _
from .models import SCDoc, RefillingCart
from index.models import CartridgeItemName, City
from .forms.add_doc import AddDoc
from .forms.edit_name import EditName
from .forms.add_city import CityF
from .forms.edit_city import CityE
from common.cbv import GridListView
from common.helpers import BreadcrumbsPath

class handbook(TemplateView):
    template_name = 'docs/handbook.html'

    @method_decorator(login_required)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        BreadcrumbsPath(args[0])
        return super(handbook, self).dispatch(*args, **kwargs)


@login_required
@never_cache
def delivery(request):
    """Списки договоров на поставку расходников
    """
    context = {}
    context['back'] = BreadcrumbsPath(request).before_page(request)
    # выбираем только договора обслуживания и поставки
    docs = SCDoc.objects.filter(departament=request.user.departament).filter( Q(doc_type=1) | Q(doc_type=2)).order_by('-pk')
    context['docs'] = docs
    if request.method == 'POST':
        form = AddDoc(request.POST)
        if form.is_valid():
            data_in_post = form.cleaned_data
            if request.GET.get('select', ''):
                # если пользователь производит редактирование и сохранение документа
                doc_id = request.GET.get('select', '')
                try:
                    doc_id = int(doc_id)
                except ValueError:
                    doc_id = 0

                try:
                    doc = SCDoc.objects.get(pk=doc_id)
                except SCDoc.DoesNotExist:
                    raise Http404

                # производим сохранения изменений
                doc.number          = data_in_post.get('number','')
                doc.date_of_signing = data_in_post.get('date','')
                doc.firm            = data_in_post.get('firm','')
                doc.title           = data_in_post.get('title','')
                doc.short_cont      = data_in_post.get('short_cont','')
                doc_type            = data_in_post.get('doc_type', '')
                doc.money           = data_in_post.get('money','')
                doc.save()
                messages.success(request, _('%(doc_num)s success saved.') % {'doc_num': doc.number})
            else:
                # если пользователь просто создаёт новый документ
                m1 = SCDoc.objects.create(
                           number          = data_in_post.get('number',''),
                           date_of_signing = data_in_post.get('date', 0),
                           date_created    = timezone.now(),
                           firm            = data_in_post.get('firm',''),
                           title           = data_in_post.get('title',''),
                           short_cont      = data_in_post.get('short_cont',''),
                           money           = data_in_post.get('money',''),
                           doc_type        = data_in_post.get('doc_type', ''),
                           departament     = request.user.departament
                           )
                messages.success(request, _('New %(doc_num)s success created.') % {'doc_num': data_in_post.get('number','')})

            context['form'] = form    
            return HttpResponseRedirect(request.path)
        else:
            context['form'] = form    
    elif request.method == 'GET':
        if request.GET.get('select', ''):
            context['edit'] = True
            doc_id = request.GET.get('select', '')
            try:
                doc_id = int(doc_id)
            except ValueError:
                doc_id = 0
            try:
                doc = SCDoc.objects.get(pk=doc_id)
            except SCDoc.DoesNotExist:
                raise Http404

            if doc.date_of_signing:
                date = str(doc.date_of_signing.day) + '/' +  str(doc.date_of_signing.month) + '/' + str(doc.date_of_signing.year)
            else:
                date = ''
            money = doc.money if doc.money else 0
            money /= 100
            form = AddDoc(initial={
                'number': doc.number,
                'title': doc.title,
                'money': money,
                'short_cont': doc.short_cont,
                'firm': doc.firm,
                'doc_type': doc.doc_type,  
                'date': date })

            context['form'] = form

        elif request.GET.get('delete', ''):
            # ветка для удаления документа
            doc_id = request.GET.get('delete', '')
            try:
                doc_id = int(doc_id)
            except ValueError:
                doc_id = 0

            try:
                doc = SCDoc.objects.get(pk=doc_id)
            except SCDoc.DoesNotExist:
                raise Http404
            
            doc_number = doc.number
            doc.delete()

            messages.error(request, _('Document %(doc_number)s deleted!') % {'doc_number': doc_number})
            return HttpResponseRedirect(reverse('docs:delivery'))

        elif request.GET.get('show', ''):
            # ветка для просотра одного конкретного договора
            doc_id = request.GET.get('show', '')
            try:
                doc_id = int(doc_id)
            except ValueError:
                doc_id = 0
            try:
                doc = SCDoc.objects.filter(departament=request.user.departament).filter(pk=doc_id)
            except SCDoc.DoesNotExist:
                raise Http404
            context['not_show_form'] = True
            context['docs'] = doc
        else:
            form = AddDoc()
            context['form'] = form
    else:
        # метод не поддерживается
        pass
    return render(request, 'docs/delivery.html', context)


@login_required
@never_cache
def edit_name(request):
    """
    """
    context = dict()
    name_id = request.GET.get('id', '')
    context['back'] = BreadcrumbsPath(request).before_page(request)
    if not name_id:
        raise Http404
    try:
        name_id = int(name_id)
    except ValueError:
        name_id = 0

    try:
        m1 =  CartridgeItemName.objects.get(pk=name_id)
    except CartridgeItemName.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = EditName(request.POST)
        if form.is_valid():
            data_in_post = form.cleaned_data
            cartName = data_in_post.get('cartName','')
            cartType = data_in_post.get('cartType','')
            comment = data_in_post.get('comment','')
            # сохраняем изменения в БД
            m1.cart_itm_name = cartName
            m1.cart_itm_type = cartType
            m1.comment       = comment
            m1.save()
            return HttpResponseRedirect(reverse('docs:view_names'))
        else:
            # если в веденных данных есть ошибка
            context['form'] = form

    else:
        # если пользователь перишёл через GET запрос
        form = EditName(initial={ 'cartName': m1.cart_itm_name, 
                            'cartType': m1.cart_itm_type, 
                            'comment': m1.comment })
        context['form'] = form
    return render(request, 'docs/edit_name.html', context)


class ViewSendActs(GridListView):
    """Просмотр списка актов передачи на заправку
    """
    @method_decorator(login_required)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(ViewSendActs, self).dispatch(*args, **kwargs)

    def get(self, request, **kwargs):
        all_acts = RefillingCart.objects.filter(departament=request.user.departament).filter(doc_type=1).order_by('-pk')
        page_size = self.items_per_page()
        self.context['page_size'] = page_size
        self.context['docs'] = self.pagination(all_acts, page_size)
        return render(request, 'docs/acts_list.html', self.context)

@login_required
@never_cache
def add_city(request):
    """Добавление города в справочник.
    """
    back = BreadcrumbsPath(request).before_page(request)
    if request.method == 'POST':
        form_obj = CityF(request.POST)
        if form_obj.is_valid():
            data_in_post = form_obj.cleaned_data
            m1 = City(city_name=data_in_post['city_name'])
            m1.save()
            messages.success(request, _('City "%(city)s" success added.') % {'city': data_in_post['city_name']})
            return redirect(reverse('docs:add_city'))
        else:
            form_obj = CityF(request.POST)
    else:
        form_obj = CityF()
    return render(request, 'docs/add_city.html', {'form': form_obj, 'back': back})

@login_required
@never_cache
def edit_city(request):
    """Редактирование названия города.
    """
    context = dict()
    context['back'] = BreadcrumbsPath(request).before_page(request)
    select = request.GET.get('select', 0)
    try:
        m1 = City.objects.get(pk=select)
    except City.DoesNotExist:
        return Http404
    if request.method == 'POST':
        form = CityE(request.POST)
        if form.is_valid():
            data_in_post = form.cleaned_data
            m1.city_name = data_in_post['city_name']
            m1.save()
            messages.success(request, _('City "%(city)s" success edited.') % {'city': data_in_post['city_name']})
            return redirect(reverse('docs:edit_city') + '?select=' + str(select))
        else:
            context['form'] = CityE(request.POST)
    else:
        context['form'] = CityE(initial={'city_name': m1.city_name,})
    return render(request, 'docs/edit_city.html', context)
