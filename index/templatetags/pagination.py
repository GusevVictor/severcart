# -*- coding:utf-8 -*-

from django import template

register = template.Library()

@register.inclusion_tag('index/found_pagination.html')
def found_pagination(items_objects, size_perpage):
    """
    Пагинация страниц в стиле foundation 4.
    Фукция на вход принимает объект Page класса Paginator.
    """
    return {
        'items': items_objects, 'spp': str(size_perpage)
    }
