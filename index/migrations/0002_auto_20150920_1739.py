# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartridgeitem',
            name='cart_uses_count',
        ),
        migrations.AddField(
            model_name='cartridgeitem',
            name='cart_filled',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
