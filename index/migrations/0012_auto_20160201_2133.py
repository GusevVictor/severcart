# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0011_cartridgeitem_delivery_doc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartridgeitem',
            name='delivery_doc',
            field=models.IntegerField(default=0, null=True, db_index=True),
        ),
    ]
