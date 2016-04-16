# -*- coding:utf-8 -*-

from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

import logging
logger = logging.getLogger('simp')

def recursiveChildren(node, level=0):
    results = [{'id': node['id'], 'level': level, 'name': node['data']['name']}]
    if node.get('children', 0) and len(node.get('children')) > 0:
        for child in node['children']:
            results.extend(recursiveChildren(child, level=level + 1))
    return results

def check_ajax_auth(any_views):
    """Проверяет является запрос от аутентифицированного пользователя. 
    """
    def wrapper(*args, **argv):
        req = args[0]
        if not req.user.is_authenticated():
            return HttpResponse(_('You are not authenticated.'), status=401)
        
        return any_views(*args, **argv)
        
    return wrapper
