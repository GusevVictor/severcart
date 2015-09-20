# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0003_auto_20150920_2004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartridgeitem',
            name='cart_code',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cartridgeitem',
            name='cart_date_added',
            field=models.DateField(blank=True, null=True),
        ),
    ]
