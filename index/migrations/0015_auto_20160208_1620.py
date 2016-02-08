# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0014_auto_20160207_2019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartridgeitemname',
            name='cart_itm_type',
            field=models.ForeignKey(to='index.CartridgeType', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
