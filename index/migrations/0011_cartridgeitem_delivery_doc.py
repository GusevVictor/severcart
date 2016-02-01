# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0010_auto_20160128_1815'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartridgeitem',
            name='delivery_doc',
            field=models.IntegerField(db_index=True, null=True),
        ),
    ]
