# -*- coding:utf-8 -*-

from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter()
def nbsp(value):
    tmp = '&nbsp;&nbsp;&nbsp;&nbsp;' * value
    return mark_safe(tmp)


@register.filter()
def dash(value):
    tmp = '|—' * value
    return mark_safe(tmp)


@register.filter
def get_range(value):
    return range(1, value )

@register.simple_tag
def navactive(request, urls):
    """Тэг для подсветки текущего пункта меню.
        Подсмотрел здесь: https://www.turnkeylinux.org/blog/django-navbar
    """
    if request.path in ( reverse(url) for url in urls.split() ):
        return "select"
    return ""


@register.filter()
def pretty_status(value):
    from index.models import STATUS 
    return mark_safe(STATUS[value-1][1])


@register.filter()
def get_parrent(value):
    """
    Извлекаем корневой(родительский) элемент MPTT Tree дерева
    """
    return value.get_root()
