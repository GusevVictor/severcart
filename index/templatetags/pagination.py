# -*- coding:utf-8 -*-

from django import template

register = template.Library()

@register.inclusion_tag('index/found_pagination.html')
def found_pagination(items_objects, size_perpage, request=None):
    """
    Пагинация страниц в стиле foundation 4.
    Фукция на вход принимает объект Page класса Paginator.
    """
    search = ''
    if request and request.GET.get('search_number', 0):
        search_number = request.GET.get('search_number')
        search = '&search_number=' + str(search_number)
    else:
        search = ''

    if request and request.GET.get('search_name', 0):
        search_name = request.GET.get('search_name')
        tmp = '&search_name=' + str(search_name)
        search += tmp

    return {
        'items': items_objects, 'spp': str(size_perpage), 'search': search ,
    }
