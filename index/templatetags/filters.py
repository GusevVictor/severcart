from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter()
def nbsp(value):
    tmp = ''
    for i in range(value):
        tmp += '&nbsp;&nbsp;&nbsp;&nbsp;'
    return mark_safe(tmp)


@register.filter()
def dash(value):
    tmp = ''
    for i in range(value):
        tmp += '|—'
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