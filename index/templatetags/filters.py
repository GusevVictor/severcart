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
    """
        Filter - returns a list containing range made from given value
        Usage (in template):

        <ul>{% for i in 3|get_range %}
          <li>{{ i }}. Do something</li>
        {% endfor %}</ul>

        Results with the HTML:
        <ul>
          <li>0. Do something</li>
          <li>1. Do something</li>
          <li>2. Do something</li>
        </ul>

        Instead of 3 one may use the variable set in the views
    """
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
