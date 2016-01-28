# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_auto_20160128_1815'),
    ]

    operations = [
        migrations.AddField(
            model_name='events',
            name='cart_index',
            field=models.IntegerField(default=1, db_index=True),
            preserve_default=False,
        ),
    ]
