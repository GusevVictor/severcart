from django.db import models


# Create your models here.
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

