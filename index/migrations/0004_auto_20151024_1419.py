# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0003_auto_20151024_1413'),
    ]

    operations = [
        migrations.RenameField(
            model_name='summary',
            old_name='empty',
            new_name='filled',
        ),
        migrations.RenameField(
            model_name='summary',
            old_name='filles',
            new_name='recycler_bin',
        ),
        migrations.AddField(
            model_name='summary',
            name='uses',
            field=models.IntegerField(default=0),
        ),
    ]
