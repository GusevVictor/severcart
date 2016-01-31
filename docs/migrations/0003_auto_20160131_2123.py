# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('docs', '0002_auto_20160131_1231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scdoc',
            name='short_cont',
            field=models.TextField(null=True),
        ),
    ]
