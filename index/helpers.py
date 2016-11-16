# -*- coding:utf-8 -*-

from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from .models import Numerator

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


class LastNumber(object):
    """Вспомогательный класс для хранения последнего присвоенного номера в СУБД.
    """
    def __init__(self, request):        
        self.request = request
        try:
            self.m1 = Numerator.objects.get(departament=request.user.departament)
        except Numerator.DoesNotExist:
            self.last_number    = 1
            self.departament    = request.user.departament
            self.m1 = Numerator(last_number=self.last_number, departament=self.departament)
        else:
            self.last_number    = self.m1.last_number
            self.departament    = self.m1.departament

    def get_num(self):
        return self.last_number

    def commit(self):
        """
        """
        self.m1.last_number = self.last_number
        self.m1.departament = self.departament
        self.m1.save()

def str2int(v):
    try:
        v = int(v)
    except:
        v = 0
    return v

def str2float(v):
    v = v.replace(',','.')
    try:
        v = float(v)
    except:
        v = 0
    return v
