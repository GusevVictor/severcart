# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('docs', '0003_auto_20160131_2123'),
    ]

    operations = [
        migrations.AddField(
            model_name='scdoc',
            name='user',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='scdoc',
            name='doc_type',
            field=models.IntegerField(choices=[(1, 'Договор поставки'), (2, 'Договор обслуживания'), (3, 'Акт передачи'), (4, 'Акт списания')], default=1),
        ),
    ]
