# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_auto_20160124_1000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='cart_action',
            field=models.IntegerField(null=True),
        ),
    ]
