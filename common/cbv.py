# -*- coding:utf-8 -*-

from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic.base import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from index.models import CartridgeItem
from .helpers import BreadcrumbsPath

import logging
logger = logging.getLogger('simp')

class GridListView(View):
    """Используется для показа списка документов.
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.context = dict()
        return super(GridListView, self).dispatch(*args, **kwargs)

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
        if not(page_size is None or page_size==''):
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

class CartridgesView(GridListView):
    """Базовый класс для показа списка картриджей.
    """
    
    @method_decorator(login_required)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        self.request = args[0]
        BreadcrumbsPath(self.request)
        self.all_items = CartridgeItem.objects.all()
        return super(CartridgesView, self).dispatch(*args, **kwargs)

    def sort_columns(self):
        """Сортировка данных на основе выбранного стобца.
        """
        #отслеживаем случай когда пользователь ушел на другой url и нужно
        # сбросить настроки сортировок.
        # при переходе на новую страницу, сбрасываем сортировки
        if self.request.session.get('back', ''):
            if self.request.META['PATH_INFO'] != self.request.session['back']:
                self.request.session['sort'] = None
                self.request.session['back'] = self.request.META['PATH_INFO']
        else:
            # инициализация при первом заходе
            self.request.session['back'] = self.request.META['PATH_INFO']
        
        select_action = self.request.GET.get('action', '')
        if select_action == 'number':
            self.context['select_number'] = True
            if self.request.session.get('sort') == 'cart_number':
                self.request.session['sort'] = '-cart_number'
                self.context['number_triangle'] = '▼'
            else:
                self.context['number_triangle'] = '▲'
                self.request.session['sort'] = 'cart_number'

        elif select_action == 'name':
            self.context['select_type'] = True
            if self.request.session.get('sort') == 'cart_itm_name':
                self.request.session['sort'] = '-cart_itm_name'
                self.context['type_triangle'] = '▼'
            else:
                self.request.session['sort'] = 'cart_itm_name'
                self.context['type_triangle'] = '▲'

        elif select_action == 'recovery':
            self.context['select_count']       = True
            if self.request.session.get('sort') == 'cart_number_refills':
                self.request.session['sort'] = '-cart_number_refills'
                self.context['count_triangle'] = '▼'
            else:
                self.request.session['sort'] = 'cart_number_refills'
                self.context['count_triangle'] = '▲'
        
        elif select_action == 'dataadd':
            self.context['select_date']   = True
            if self.request.session.get('sort') == 'cart_date_added':
                self.request.session['sort'] = '-cart_date_added'
                self.context['date_triangle'] = '▼'
            else:
                self.request.session['sort'] = 'cart_date_added'
                self.context['date_triangle'] = '▲'

        elif select_action == 'change_date':
            self.context['select_change_date']   = True
            if self.request.session.get('sort') == 'cart_date_change':
                self.request.session['sort'] = '-cart_date_change'
                self.context['datec_triangle'] = '▼'
            else:
                self.request.session['sort'] = 'cart_date_change'
                self.context['datec_triangle'] = '▲'
        else:
            # переходим в веточку если пользователь не выбирал сортировок
            # дальнейшие преобразования производим на основе предыдущих действий, если они были
            sort_order = self.request.session.get('sort', '')
            if sort_order == 'cart_number' or sort_order == '-cart_number':
                self.context['select_number'] = True
                self.context['number_triangle'] = '▲' if sort_order == 'cart_number' else '▼'
            elif sort_order == 'cart_itm_name' or sort_order == '-cart_itm_name':
                self.context['select_type'] = True
                self.context['type_triangle'] = '▲' if sort_order == 'cart_itm_name' else '▼'
            elif sort_order == 'cart_number_refills' or sort_order == '-cart_number_refills':
                self.context['select_count']  = True
                self.context['count_triangle'] = '▲' if sort_order == 'cart_number_refills' else '▼'
            elif sort_order == 'cart_date_added' or sort_order == '-cart_date_added':
                self.context['select_date']   = True
                self.context['date_triangle'] = '▲' if sort_order == 'cart_date_added' else '▼'
            elif sort_order == 'cart_date_change' or sort_order == '-cart_date_change':
                self.context['select_change_date']   = True
                self.context['datec_triangle'] = '▲' if sort_order == 'cart_datec_added' else '▼'
            else:
                # по умолчанию будем сортивать по id в порядке возрастания номеров
                self.context['select_number'] = True
                self.request.session['sort'] = 'cart_number'
                self.context['number_triangle'] = '▲'

    def search_num(self):
        """Работаем с поисковой формой по номеру картриджа
        """
        search_number  = self.request.GET.get('search_number')
        self.all_items = self.all_items.order_by(self.request.session['sort'])
        if not(search_number is None or search_number == ''):
            search_number = str(search_number).strip()
            self.all_items = self.all_items.filter(Q(cart_number__icontains=search_number))
            self.context['search_number'] = search_number

    def search_name(self):
        """Работаем с поисковой формой по имени картриджа
        """
        search_name  = self.request.GET.get('search_name')
        self.all_items = self.all_items.order_by(self.request.session['sort'])
        if not(search_name is None or search_name == ''):
            search_name = str(search_name).strip()
            self.all_items = self.all_items.filter(Q(cart_itm_name__cart_itm_name__icontains=search_name))
            self.context['search_name'] = search_name
    
    def get(self):
        """Избавляем себя от дублирований.
        """
        self.sort_columns()
        self.search_num()
        self.search_name()
