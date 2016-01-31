from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def divide(value):
    rubl = value // 100
    kop  =  value - rubl*100
    if kop:
    	tmp = '%s,%s' % (rubl, kop,)
    else:
    	tmp = str(rubl)
    return mark_safe(tmp)
