from django.db import models
from treebeard.ns_tree import NS_Node

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


class CartridgeOwner(models.Model):
    owner = models.TextField()

class CartridgeItemName(models.Model):
    cart_itm_name = models.CharField(max_length=256)
    cart_itm_type = models.ForeignKey(CartridgeType)

    def __str__(self):
        return self.cart_itm_name


class CartridgeItem(models.Model):
    cart_itm_name = models.ForeignKey(CartridgeItemName, blank=True, null=True)
    cart_date_added = models.DateField(blank=True, null=True)
    cart_owner = models.ForeignKey(Category, blank=True, null=True)
    cart_code = models.IntegerField(blank=True, null=True)
    cart_filled = models.BooleanField()   # логический флаг, сигнализирующий о заполненнности
    node_order_by = ['id']
