# -*- coding:utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

class Events(models.Model):
    """Список событий, использется для генерации различных отчётов.
    """

    ETYPE_CHOICES = (
        ('AD', _('Adding a new consumables')),
        ('ADE', _('Adding a new empty cartriges')),
        ('TR', _('Transfer consumables for use')),
        ('TF', _('Transfer Consumables for refueling')),
        ('RS', _('Return to the remanufactured cartridge on storage')),
        ('TB', _('Move to basket')),
        ('DC', _('Delete cartridge')),
        ('TS', _('Passing an empty consumables stock')),
        ('CU', _('Creating a new user')),
        ('DU', _('Removing a user')),
    )
    # устанавливаем слабую связанность для объектов
    date_time   = models.DateTimeField()
    cart_index = models.IntegerField(db_index=True)  # номер назначает база данных
    cart_number = models.IntegerField(db_index=True) # условный номер генерируемый при создании объекта, возможна смена
    cart_type   = models.CharField(max_length=256, null=True)
    cart_action = models.IntegerField(null=True)
    # cart_action хранит данные о восстановительных действиях с объектом 5 значном числе.
    # 1 в 5 разряде - заправка и очитска
    # 1 в 4 разряде - замена фотовала
    # 1 в 3 разряде - замена ракеля
    # 1 в 2 разряде - замена чипа
    # 1 в 1 разряде - замена магнитного вала
    # если действий не производилось, то в соответствующем разряде ставится 0
    event_type  = models.CharField(choices=ETYPE_CHOICES, max_length=32)
    event_user  = models.CharField(max_length=64)
    event_org   = models.CharField(max_length=256, null=True)
    event_firm  = models.CharField(max_length=256, null=True)
    departament = models.IntegerField()
