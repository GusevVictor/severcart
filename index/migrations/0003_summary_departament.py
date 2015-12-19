# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0002_auto_20151121_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='summary',
            name='departament',
            field=models.ForeignKey(to='index.OrganizationUnits', default=26),
            preserve_default=False,
        ),
    ]
