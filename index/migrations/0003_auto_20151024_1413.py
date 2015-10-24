# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0002_auto_20151024_1401'),
    ]

    operations = [
        migrations.AlterField(
            model_name='summary',
            name='empty',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='summary',
            name='empty_on_stock',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='summary',
            name='filles',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='summary',
            name='full_on_stock',
            field=models.IntegerField(default=0),
        ),
    ]
