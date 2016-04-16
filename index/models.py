# -*- coding:utf-8 -*-

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import ugettext_lazy as _


class OrganizationUnits(MPTTModel):
    name = models.CharField(max_length=254)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


class CartridgeType(models.Model):
    cart_type = models.CharField(max_length=256, verbose_name=_('The name of the new type'))
    comment = models.TextField(_('Comment'), blank=True)

    def __str__(self):
        return self.cart_type


class CartridgeItemName(models.Model):
    cart_itm_name = models.CharField(max_length=256, db_index=True)
    cart_itm_type = models.ForeignKey(CartridgeType, on_delete=models.PROTECT)
    comment = models.TextField(_('Comment'), blank=True)

    def __str__(self):
        return self.cart_itm_name


class City(models.Model):
    city_name = models.CharField(_('Enter the name of the city'), max_length=256)

    def __str__(self):
        return self.city_name


class FirmTonerRefill(models.Model):
    """
    Хранит списки фирм занимающиеся заправкой и восстановление
    картриджей.
    """
    firm_name = models.CharField(_('Name'), max_length=256)
    firm_city = models.ForeignKey(City, verbose_name=_('Select city'))
    firm_contacts = models.TextField(_('Contacts'), null=True)
    firm_address = models.TextField(_('Address'), null=True)
    firm_comments = models.TextField(_('Comment'), null=True)

    def __str__(self):
        return self.firm_name

STATUS = (
        (1, _('Full and in stock')),
        (2, _('In use')),
        (3, _('Empty and in stock')),
        (4, _('On restoration')),
        (5, _('Full and in basket')),
        (6, _('Empty and in basket')),
    )


class CartridgeItem(models.Model):
    cart_number = models.IntegerField(db_index=True, null=True)
    cart_number_prefix  = models.CharField(max_length=256, null=True)
    cart_number_postfix = models.CharField(max_length=256, null=True)
    cart_itm_name = models.ForeignKey(CartridgeItemName, on_delete=models.PROTECT)
    cart_date_added = models.DateField(db_index=True)
    cart_date_change = models.DateField(db_index=True)
    departament = models.ForeignKey(OrganizationUnits, blank=True, null=True, on_delete=models.PROTECT)
    cart_status = models.IntegerField(choices=STATUS, default=1)
    cart_number_refills = models.IntegerField(default=0, db_index=True)
    filled_firm = models.ForeignKey(FirmTonerRefill, null=True, on_delete=models.PROTECT,)
    comment = models.TextField(_('Comment'), blank=True)
    delivery_doc = models.IntegerField(db_index=True, null=True, default=0)
    node_order_by = ['pk']
