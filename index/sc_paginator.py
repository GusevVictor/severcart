# -*- coding:utf-8 -*-

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import logging
logger = logging.getLogger('simp')


def sc_paginator(all_items, request, size_perpage):
    """Система пагинации.
    """
    paginator = Paginator(all_items, size_perpage)
    page = request.GET.get('page')
    try:
        cartridjes = paginator.page(page)
    except PageNotAnInteger:
        cartridjes = paginator.page(1)
    except EmptyPage:
        cartridjes = paginator.page(paginator.num_pages)

    return cartridjes
