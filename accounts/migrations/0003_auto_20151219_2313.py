# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20151121_2322'),
    ]

    operations = [
        migrations.RenameField(
            model_name='anconuser',
            old_name='department',
            new_name='departament',
        ),
    ]
