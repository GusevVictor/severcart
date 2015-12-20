# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0003_summary_departament'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartridgeitem',
            name='cart_filled',
        ),
        migrations.AddField(
            model_name='cartridgeitem',
            name='cart_status',
            field=models.IntegerField(choices=[(1, 'Full in stock'), (2, 'In use'), (3, 'Empty in stock'), (4, 'Filled in firm')], default=1),
        ),
    ]
