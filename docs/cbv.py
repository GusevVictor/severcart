# -*- coding:utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from index.models import CartridgeItemName

class GridNamesView(View):
    """
    """
    context = dict()

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GridNamesView, self).dispatch(*args, **kwargs)

    def pagination(self, all_items, size_perpage):
        paginator = Paginator(all_items, size_perpage)
        page = self.request.GET.get('page')
        try:
            objects = paginator.page(page)
        except PageNotAnInteger:
            objects = paginator.page(1)
        except EmptyPage:
            objects = paginator.page(paginator.num_pages)
        return objects

    def items_per_page(self):
        # работаем с выводом количеством элементов на страницу
        page_size = self.request.GET.get('page_size', '')
        if not(page_size == None or page_size==''):
            try:
                page_size = int(page_size)
            except ValueError:
                pass
            else:
                page_size = 10000000 if page_size == 0 else page_size
                self.request.session['page_size'] = page_size
        else:
            page_size = self.request.session.get('page_size', 12)
        return page_size


class NamesView(GridNamesView):
    """
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NamesView, self).dispatch(*args, **kwargs)

    def get(self, request,**kwargs):
        all_names = CartridgeItemName.objects.all().order_by('pk')
        page_size = self.items_per_page()
        self.context['page_size'] = page_size
        self.context['items'] = self.pagination(all_names, page_size)
        return render(request, 'docs/names_list.html', self.context)
