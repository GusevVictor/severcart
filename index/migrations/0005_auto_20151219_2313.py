# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0004_auto_20151219_2147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartridgeitem',
            name='cart_status',
            field=models.IntegerField(default=1, choices=[(1, 'Full in stock'), (2, 'In use'), (3, 'Empty in stock'), (4, 'Filled in firm'), (5, 'Deleted')]),
        ),
    ]
