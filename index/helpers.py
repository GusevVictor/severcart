# -*- coding:utf-8 -*-
from django.http import HttpResponse
from django.contrib.sessions.models import Session
from accounts.models import AnconUser
#from .models import Summary

import logging
logger = logging.getLogger('simp')


def recursiveChildren(node, level=0):
    results = [{'id': node['id'], 'level': level, 'name': node['data']['name']}]
    if node.get('children', 0) and len(node.get('children')) > 0:
        for child in node['children']:
            results.extend(recursiveChildren(child, level=level + 1))
    return results


class Dashboard(object):
    """Служебный класс для наполнения таблицы Summary. TODO сделать синглетоном!
    """
    def __init__(self, request):
        self.departament = request.user.departament
        self.m1 = Summary.objects.filter(departament=self.departament)
        if self.m1:
            self.m1 = self.m1[0]
        else:
            self.m1 = Summary(full_on_stock=0,
                                empty_on_stock=0,
                                uses=0,
                                filled=0,
                                departament=self.departament)
            self.m1.save()
        self.full_on_stock  = self.m1.full_on_stock
        self.empty_on_stock = self.m1.empty_on_stock
        self.uses           = self.m1.uses
        self.filled         = self.m1.filled
        self.recycler_bin   = self.m1.recycler_bin
        

    def add_full_to_stock(self,num=0):
        """Добавляет N количество новых картриджей на склад
        """ 
        m1 = Summary.objects.filter(departament=self.departament)
        m1 = m1[0]
        m1.full_on_stock = m1.full_on_stock + num
        m1.save(update_fields=['full_on_stock'])

    def tr_cart_to_uses(self, num=0):
        """Передача N кол-во картриджей в пользование.  
        """
        if num > self.full_on_stock:
            raise ValueError('Превышено максимальное кол-во единиц!')
        self.full_on_stock = self.full_on_stock - num
        self.uses = self.uses + num 
        self.m1.full_on_stock = self.full_on_stock
        self.m1.uses = self.uses
        self.m1.save(update_fields=['uses', 'full_on_stock'])

    def tr_empty_cart_to_stock(self, num):
        """Забрать пуст(ой)(ые) картридж(и) у пользователя на склад. 
        """
        if num > self.uses:
            raise ValueError('Невозможно изъять расходный материал.')
        self.uses = self.uses - num
        self.empty_on_stock = self.empty_on_stock + num
        self.m1.empty_on_stock = self.empty_on_stock
        self.m1.uses = self.uses
        self.m1.save(update_fields=['empty_on_stock', 'uses'])

    def tr_empty_cart_to_firm(self, num=0):
        """ Передача пустых картриджей на заправку и возможно восстановление.
            Как договоритесь ;)
        """
        if num > self.empty_on_stock:
            raise ValueError('Невозможно передать больше чем есть на складе.')

        self.empty_on_stock = self.empty_on_stock - num
        self.filled = self.filled + num
        self.m1.empty_on_stock = self.empty_on_stock
        self.m1.filled = self.filled
        self.m1.save()              

    def tr_filled_cart_to_stock(self, num=0):
        """Перемещение заправленных картриджей обратно на склад.
        """
        if num > self.filled:
            raise ValueError('Невозможно забрать больше, чем передано')
        self.full_on_stock = self.full_on_stock + num
        self.filled = self.filled - num
        self.m1.full_on_stock = self.full_on_stock
        self.m1.filled = self.filled
        self.m1.save(update_fields=['filled', 'full_on_stock'])      

    def tr_full_stock_to_basket(self, num=0):
        """Перемещаем заполненные картриджи в корзину. 
        """
        self.full_on_stock    = self.full_on_stock - num
        self.recycler_bin     = self.recycler_bin  + num
        self.m1.full_on_stock = self.full_on_stock
        self.m1.recycler_bin  = self.recycler_bin
        self.m1.save(update_fields=['recycler_bin', 'full_on_stock'])

    def tr_from_basket_to_sock(self, num=0):
        """Перемащаем картридж из корзины обратно на склад. Ну вдруг пользователь
           передумал. 
        """
        self.full_on_stock    = self.full_on_stock + num
        self.recycler_bin     = self.recycler_bin  - num
        self.m1.full_on_stock = self.full_on_stock
        self.m1.recycler_bin  = self.recycler_bin
        self.m1.save(update_fields=['recycler_bin', 'full_on_stock'])

    def tr_empty_uses_to_basket(self, num=0):
        """Перемещаем картридж из пользования в корзину.
        """
        self.m1.recycler_bin = self.recycler_bin + num
        self.m1.uses         = self.uses - num
        self.m1.save(update_fields=['recycler_bin', 'uses'])

    def clear_basket(self, num=0):
        """Очищаем корзину.
        """
        self.m1.recycler_bin = self.recycler_bin  - num
        self.m1.save(update_fields=['recycler_bin'])


    def tr_empty_stock_to_basket(self, num=0):
        """Перемещаем пустые картриджи в корзину.
        """
        pass

def check_ajax_auth(any_views):
    """
    Проверяет является запрос от аутентифицированного пользователя. 
    """
    def wrapper(*args, **argv):
        req = args[0]
        if not req.user.is_authenticated():
            return HttpResponse('Вы не аутентифицированы.', status=401)
        
        return any_views(*args, **argv)
        
    return wrapper
    