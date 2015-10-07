from django import template

register = template.Library()

@register.inclusion_tag('index/found_pagination.html')
def found_pagination(items_objects):
    """
    Пагинация страниц в стиле foundation 4.
    Фукция на вход принимает объект Page класса Paginator.
    """
    return {
        'items': items_objects,
    }
