# -*- coding:utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from common.cbv import GridListView
from index.models import CartridgeItemName, CartridgeType


class NamesView(GridListView):
    """Просмотр списка названий расходных материалов.
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


class TypesView(GridListView):
    """Просмотр списка типов расходных материалов.
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TypesView, self).dispatch(*args, **kwargs)

    def get(self, request,**kwargs):
        all_names = CartridgeType.objects.all().order_by('pk')
        page_size = self.items_per_page()
        self.context['page_size'] = page_size
        self.context['items'] = self.pagination(all_names, page_size)
        return render(request, 'docs/types_list.html', self.context)

