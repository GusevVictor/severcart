# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0009_cartridgeitem_cart_date_change'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartridgeitem',
            name='cart_number',
            field=models.IntegerField(db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='cartridgeitem',
            name='cart_number_postfix',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='cartridgeitem',
            name='cart_number_prefix',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='cartridgeitem',
            name='cart_date_added',
            field=models.DateField(db_index=True),
        ),
        migrations.AlterField(
            model_name='cartridgeitem',
            name='cart_date_change',
            field=models.DateField(db_index=True),
        ),
        migrations.AlterField(
            model_name='cartridgeitem',
            name='cart_number_refills',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]
