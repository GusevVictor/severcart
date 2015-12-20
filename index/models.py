# -*- config:utf-8 -*-

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import User


class OrganizationUnits(MPTTModel):
    name = models.CharField(max_length=254)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

class CartridgeType(models.Model):
    cart_type = models.CharField(max_length=256, verbose_name='Название нового типа')

    def __str__(self):
        return self.cart_type

class CartridgeItemName(models.Model):
    cart_itm_name = models.CharField(max_length=256)
    cart_itm_type = models.ForeignKey(CartridgeType)

    def __str__(self):
        return self.cart_itm_name


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


class CartridgeItem(models.Model):
    STATUS = (
        (1, 'Full in stock'),
        (2, 'In use'),
        (3, 'Empty in stock'),
        (4, 'Filled in firm'),
        (5, 'Deleted'),
    )
    cart_itm_name = models.ForeignKey(CartridgeItemName)
    cart_date_added = models.DateField()
    departament = models.ForeignKey(OrganizationUnits, blank=True, null=True)
    cart_status = models.IntegerField(choices=STATUS, default=1)
    cart_number_refills = models.IntegerField(default=0)
    filled_firm = models.ForeignKey(FirmTonerRefill, null=True)
    node_order_by = ['id']


class Summary(models.Model):
    """Кэш таблица с текущим состоянем БД
    """
    full_on_stock = models.IntegerField(default=0)
    empty_on_stock = models.IntegerField(default=0)
    uses = models.IntegerField(default=0)
    filled = models.IntegerField(default=0)
    recycler_bin = models.IntegerField(default=0)
    departament = models.ForeignKey(OrganizationUnits)

class Events(models.Model):
    """Список событий, использется для статистики и на морде сайта
    """
    ETYPE_CHOICES = (
        (1, 'Добавление нового расходника'),
        (2, 'Передача расходника в пользование'),
        (3, 'Передача расходники на заправку'),
        (4, 'Утилизация'),
        (5, 'Передача пустого расходника на склад'),
        (6, 'Создание нового пользователя'),
        (7, 'Удаление пользователя'),
    )
    event_type = models.IntegerField(choices=ETYPE_CHOICES)
    date_time = models.DateTimeField()
    cart_itm = models.ForeignKey(CartridgeItem, null=True)
    comment = models.CharField(max_length=256)
