# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0013_auto_20160207_1525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartridgeitem',
            name='cart_itm_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.CartridgeItemName'),
        ),
        migrations.AlterField(
            model_name='cartridgeitem',
            name='departament',
            field=models.ForeignKey(null=True, to='index.OrganizationUnits', blank=True, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='cartridgeitem',
            name='filled_firm',
            field=models.ForeignKey(to='index.FirmTonerRefill', null=True, on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
