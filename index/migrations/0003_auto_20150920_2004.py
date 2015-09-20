# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0002_auto_20150920_1739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartridgeitem',
            name='cart_owner',
            field=models.ForeignKey(to='index.Category', null=True, blank=True),
        ),
    ]
