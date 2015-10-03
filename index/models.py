# -*- config:utf-8 -*-

from django.db import models
from treebeard.ns_tree import NS_Node
from django.contrib.auth.models import User

class Category(NS_Node):
    """
    Структура организации
    """
    name = models.CharField(max_length=30)
    node_order_by = ['id']

    def __str__(self):
        return self.name


class CartridgeType(models.Model):
    cart_type = models.CharField(max_length=256)

    def __str__(self):
        return self.cart_type

class CartridgeItemName(models.Model):
    cart_itm_name = models.CharField(max_length=256)
    cart_itm_type = models.ForeignKey(CartridgeType)

    def __str__(self):
        return self.cart_itm_name


class CartridgeItem(models.Model):
    cart_itm_name = models.ForeignKey(CartridgeItemName, blank=True, null=True)
    cart_date_added = models.DateField(blank=True, null=True)
    cart_owner = models.ForeignKey(Category, blank=True, null=True)
    cart_filled = models.BooleanField()   # логический флаг, сигнализирующий о заполненнности
    node_order_by = ['id']


class City(models.Model):
    city_name = models.CharField('Введите название города', max_length=256)

    def __str__(self):
        return self.city_name


class FirmTonerRefill(models.Model):
    """
    Хранит списки фирм занимающиеся заправкой и восстановление
    картриджей.
    """
    firm_name = models.CharField('Название', max_length=256)
    firm_city = models.ForeignKey(City, blank=True, verbose_name="Выберите город")
    firm_contacts = models.TextField('Контакты', blank=True)
    firm_address = models.TextField('Адресс', blank=True)
    firm_comments = models.TextField('Комментарии', blank=True)

    def __str__(self):
        return self.firm_name

# class AnconUser(User):
#     """
#     Немножко меняем стандартную модель User.
#     """
#   #  user = models.OneToOneField(User, on_delete=models.CASCADE)
#     department = models.ForeignKey(Category, blank=True, null=True)
#     patronymic = models.CharField('Отчество', max_length=256, blank=True, null=True)
#     date_created = models.DateTimeField(blank=True, null=True)
