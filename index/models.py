# -*- config:utf-8 -*-

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import User
#from docs.models import SCDoc


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
        (5, 'Full in basket'),
        (6, 'Empty in basket'),
    )
    cart_number = models.IntegerField(db_index=True, null=True)
    cart_number_prefix  = models.CharField(max_length=256, null=True)
    cart_number_postfix = models.CharField(max_length=256, null=True)
    cart_itm_name = models.ForeignKey(CartridgeItemName)
    cart_date_added = models.DateField(db_index=True)
    cart_date_change = models.DateField(db_index=True)
    departament = models.ForeignKey(OrganizationUnits, blank=True, null=True)
    cart_status = models.IntegerField(choices=STATUS, default=1)
    cart_number_refills = models.IntegerField(default=0, db_index=True)
    filled_firm = models.ForeignKey(FirmTonerRefill, null=True)
    comment = models.TextField('Комментарий', blank=True)
    delivery_doc = models.IntegerField(db_index=True, null=True, default=0)
    node_order_by = ['pk']
