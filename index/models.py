from django.db import models
from treebeard.ns_tree import NS_Node


class CartridgeType(models.Model):
    cart_type = models.CharField(max_length=256)

    def __str__(self):
        return self.cart_type


class CartridgeOwner(models.Model):
    owner = models.TextField()


class CartridgeItem(models.Model):
    cart_type = models.ForeignKey(CartridgeType)
    cart_name = models.CharField(max_length=256)
    cart_date_added = models.DateField()
    cart_owner = models.ForeignKey(CartridgeOwner, blank=True, null=True)
    cart_code = models.IntegerField()
    cart_uses_count = models.IntegerField()


class Category(NS_Node):
    name = models.CharField(max_length=30)

    node_order_by = ['name']

    def __str__(self):
        return 'Категория: %s' % self.name
