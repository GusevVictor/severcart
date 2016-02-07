# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0012_auto_20160201_2133'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartridgeitemname',
            name='comment',
            field=models.TextField(verbose_name='Комментарий', blank=True),
        ),
        migrations.AddField(
            model_name='cartridgetype',
            name='comment',
            field=models.TextField(verbose_name='Комментарий', blank=True),
        ),
        migrations.AlterField(
            model_name='cartridgeitem',
            name='cart_status',
            field=models.IntegerField(default=1, choices=[(1, 'Полон и на складе'), (2, 'Задействован'), (3, 'Пуст и на складе'), (4, 'Заправляется'), (5, 'Полон и в корзине'), (6, 'Пуст и в корзине')]),
        ),
    ]
