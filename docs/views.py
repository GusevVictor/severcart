# -*- coding:utf-8 -*-

import datetime
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.utils import timezone
from .models import SCDoc
from index.models import CartridgeItemName
from .forms.add_doc import AddDoc
from .forms.edit_name import EditName
from common.cbv import GridListView
from common.helpers import BreadcrumbsPath

class handbook(TemplateView):
    template_name = 'docs/handbook.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(handbook, self).dispatch(*args, **kwargs)


@login_required
def service(request):
    """Списки договоров на обслуживание
    """
    return HttpResponse('<h1>Договора обслуживания</h1>')


@login_required
def delivery(request):
    """Списки договоров на поставку расходников
    """
    context = {}
    docs = SCDoc.objects.filter(departament=request.user.departament).filter(doc_type=1).order_by('-pk')
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
                doc.number = data_in_post.get('number','')
                doc.date = data_in_post.get('date','')
                doc.firm = data_in_post.get('firm','')
                doc.title = data_in_post.get('title','')
                doc.short_cont = data_in_post.get('short_cont','')
                doc.money = data_in_post.get('money','')
                doc.save()
                messages.success(request, 'Документ %s успешно сохранён.' % (doc.number, ))
            else:
                # если пользователь просто создаёт новый документ
                doc = SCDoc(number = data_in_post.get('number',''),
                           date = data_in_post.get('date',''),
                           firm = data_in_post.get('firm',''),
                           title = data_in_post.get('title',''),
                           short_cont = data_in_post.get('short_cont',''),
                           money = data_in_post.get('money',''),
                           departament = request.user.departament,
                           doc_type = 1,
                           )
                doc.save()
                messages.success(request, 'Новый %s документ успешно создан.' % (doc.number,))
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

            date = str(doc.date.day) + '/' +  str(doc.date.month) + '/' + str(doc.date.year)
            money = doc.money / 100
            form = AddDoc(initial={
                'number': doc.number,
                'title': doc.title,
                'money': money,
                'short_cont': doc.short_cont,
                'firm': doc.firm,
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
            messages.error(request, 'Документ %s удалён!' % (doc_number,))
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
    def dispatch(self, *args, **kwargs):
        return super(ViewSendActs, self).dispatch(*args, **kwargs)

    def get(self, request, **kwargs):
        all_acts = SCDoc.objects.filter(doc_type=3).filter(departament=request.user.departament).order_by('pk')
        page_size = self.items_per_page()
        self.context['page_size'] = page_size
        self.context['docs'] = self.pagination(all_acts, page_size)
        return render(request, 'docs/acts_list.html', self.context)
