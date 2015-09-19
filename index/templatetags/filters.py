from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter()
def nbsp(value):
    tmp = ''
    for i in range(value):
        tmp += '&nbsp;&nbsp;&nbsp;&nbsp;'
    return mark_safe(tmp)
