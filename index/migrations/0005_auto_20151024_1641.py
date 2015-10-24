# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0004_auto_20151024_1419'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartridgeitem',
            name='filled_firm',
            field=models.ForeignKey(to='index.FirmTonerRefill', null=True),
        ),
        migrations.AlterField(
            model_name='cartridgeitem',
            name='cart_number_refills',
            field=models.IntegerField(default=0),
        ),
    ]
