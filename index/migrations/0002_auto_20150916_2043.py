# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartridgeitem',
            name='cart_owner',
            field=models.ForeignKey(to='index.CartridgeOwner', blank=True),
        ),
    ]
