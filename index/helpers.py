# -*- coding:utf-8 -*-
from django.http import HttpResponse
from django.contrib.sessions.models import Session
from accounts.models import AnconUser
from .models import Summary

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
	def __init__(self):
		self.full_on_stock = Summary.objects.get(pk=1).full_on_stock
		self.empty_on_stock = Summary.objects.get(pk=1).empty_on_stock
		self.uses = Summary.objects.get(pk=1).uses
		self.filled = Summary.objects.get(pk=1).filled

	def add_full_to_stock(self,num=0):
		"""Добавляет N количество новых картриджей на склад
		"""	
		self.full_on_stock = self.full_on_stock + num
		m1 = Summary.objects.get(pk=1)
		m1.full_on_stock = self.full_on_stock
		m1.save()

	def tr_cart_to_uses(self, num=0):
		"""Передача N кол-во картриджей в пользование.	
		"""
		if num > self.full_on_stock:
			raise ValueError('Превышено максимальное кол-во единиц!')
		self.full_on_stock = self.full_on_stock - num
		self.uses = self.uses + num 
		m1 = Summary.objects.get(pk=1)
		m1.full_on_stock = self.full_on_stock
		m1.uses = self.uses
		m1.save()

	def tr_empty_cart_to_stock(self):
		"""Забрать пуст(ой)(ые) картридж(и) у пользователя на склад. 
		"""
		num = 1
		if self.uses:
			raise ValueError('Невозможно изъять расходный материал.')
		self.uses = self.uses - num
		self.empty_on_stock = self.empty_on_stock + num
		m1 = Summary.objects.get(pk=1)
		m1.uses = self.uses
		m1.empty_on_stock = self.empty_on_stock
		m1.save()

	def tr_empty_cart_to_firm(self, num=0):
		"""	Передача пустых картриджей на заправку и возможно восстановление.
			Как договоритесь ;)
		"""
		if num > self.empty_on_stock:
			raise ValueError('Невозможно передать больше чем есть на складе.')

		self.empty_on_stock = self.empty_on_stock - num
		self.filled = self.filled + num
		m1 = Summary.objects.get(pk=1)
		m1.empty_on_stock = self.empty_on_stock
		m1.filled = self.filled
		m1.save()		 		

	def tr_filled_cart_to_stock(self, num=0):
		"""Перемещение заправленных картриджей обратно на склад.
		"""
		if num > self.filled:
			raise ValueError('Невозможно забрать больше, чем передано')
		self.full_on_stock = self.full_on_stock + num
		self.filled = self.filled - num
		m1 = Summary.objects.get(pk=1)
		m1.full_on_stock = self.full_on_stock
		m1.filled = self.filled
		m1.save()		


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
    