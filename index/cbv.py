# -*- coding:utf-8 -*-

import json
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.sessions.models import Session
from django.db.models import Q
from django.views.generic.list import ListView
from .forms.add_cartridge_name import AddCartridgeName
from .forms.add_items import AddItems
from .forms.add_city import CityF
from .forms.add_type import AddCartridgeType
from .forms.add_firm import FirmTonerRefillF
from .forms.comment import EditCommentForm
from .models import CartridgeType
from accounts.models import AnconUser
from django.contrib.auth.models import User
from .models import CartridgeItem
from .models import OrganizationUnits
from .models import City as CityM
from .models import FirmTonerRefill
from .models import CartridgeItemName
from .helpers import recursiveChildren, check_ajax_auth
from .sc_paginator import sc_paginator
from .signals import ( sign_add_full_to_stock, 
                    sign_tr_cart_to_uses, 
                    sign_tr_cart_to_basket,
                    sign_tr_empty_cart_to_stock,
                    sign_tr_empty_cart_to_firm,
                    sign_tr_filled_cart_to_stock )

import logging
logger = logging.getLogger('simp')

class SeverCartView(ListView):
    """
    """
    def get_queryset(self):
        return

    def get_context_data(self, **kwargs):
        context = super(SeverCartView, self).get_context_data(**kwargs)
        select_action = self.request.GET.get('action', '')
        if select_action == 'number':
            context['select_number'] = True
            if self.request.session.get('sort') == 'cart_number':
                self.request.session['sort'] = '-cart_number'
                context['number_triangle'] = '▼'
            else:
                context['number_triangle'] = '▲'
                self.request.session['sort'] = 'cart_number'

        elif select_action == 'name':
            context['select_type'] = True
            if self.request.session.get('sort') == 'cart_itm_name':
                self.request.session['sort'] = '-cart_itm_name'
                context['type_triangle'] = '▼'
            else:
                self.request.session['sort'] = 'cart_itm_name'
                context['type_triangle'] = '▲'

        elif select_action == 'recovery':
            context['select_count']  = True
            if self.request.session.get('sort') == 'cart_number_refills':
                self.request.session['sort'] = '-cart_number_refills'
                context['count_triangle'] = '▼'
            else:
                self.request.session['sort'] = 'cart_number_refills'
                context['count_triangle'] = '▲'
        
        elif select_action == 'dataadd':
            context['select_date']   = True
            if self.request.session.get('sort') == 'cart_date_added':
                self.request.session['sort'] = '-cart_date_added'
                context['date_triangle'] = '▼'
            else:
                self.request.session['sort'] = 'cart_date_added'
                context['date_triangle'] = '▲'

        elif select_action == 'change_date':
            context['select_change_date']   = True
            if self.request.session.get('sort') == 'cart_date_change':
                self.request.session['sort'] = '-cart_date_change'
                context['datec_triangle'] = '▼'
            else:
                self.request.session['sort'] = 'cart_date_change'
                context['datec_triangle'] = '▲'
        else:
            # переходим в веточку если пользователь не выбирал сортировок
            # дальнейшие преобразования производим на основе предыдущих действий, если они были
            sort_order = self.request.session.get('sort')
            if sort_order == 'cart_number' or sort_order == '-cart_number':
                context['select_number'] = True
                context['number_triangle'] = '▲' if sort_order == 'cart_number' else '▼'
            elif sort_order == 'cart_itm_name' or sort_order == '-cart_itm_name':
                context['select_type'] = True
                context['type_triangle'] = '▲' if sort_order == 'cart_itm_name' else '▼'
            elif sort_order == 'cart_number_refills' or sort_order == '-cart_number_refills':
                context['select_count']  = True
                context['count_triangle'] = '▲' if sort_order == 'cart_number_refills' else '▼'
            elif sort_order == 'cart_date_added' or sort_order == '-cart_date_added':
                context['select_date']   = True
                context['date_triangle'] = '▲' if sort_order == 'cart_date_added' else '▼'
            elif sort_order == 'cart_date_change' or sort_order == '-cart_date_change':
                context['select_change_date']   = True
                context['datec_triangle'] = '▲' if sort_order == 'cart_datec_added' else '▼'
            else:
                # по умолчанию будем сортивать по id в порядке возрастания номеров
                context['select_number'] = True
                self.request.session['sort'] = 'cart_number'
                context['number_triangle'] = '▲' if sort_order == 'cart_number' else '▼'
        # работаем с поисковой формой по номеру картриджа
        search_number  = self.request.GET.get('search_number')
        self.all_items = CartridgeItem.objects.all()
        self.all_items = self.all_items.order_by(self.request.session['sort'])
        if not(search_number == None or search_number == ''):
            try:
                search_number = int(search_number)
            except ValueError:
                pass
            else:
                self.all_items = self.all_items.filter(Q(cart_number=search_number))
            context['search_number'] = search_number

        # работаем с выводом количеством элементов на страницу
        page_size = self.request.GET.get('page_size', '')
        if not(page_size == None or page_size==''):
            try:
                page_size = int(page_size)
            except ValueError:
                pass
            else:
                page_size = 10000000 if page_size == 0 else page_size
                self.size_perpage = page_size
                self.request.session['page_size'] = page_size
        else:
            self.size_perpage = self.request.session.get('page_size', 12)
        return context
