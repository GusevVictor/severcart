# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='anconuser',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='anconuser',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='anconuser',
            name='patronymic',
        ),
        migrations.AddField(
            model_name='anconuser',
            name='fio',
            field=models.CharField(null=True, verbose_name='Фамилие Имя Отчество', max_length=256, blank=True),
        ),
    ]
