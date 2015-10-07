# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='anconuser',
            name='first_name',
            field=models.CharField(verbose_name='Имя', blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='anconuser',
            name='last_name',
            field=models.CharField(verbose_name='Фамилие', blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='anconuser',
            name='patronymic',
            field=models.CharField(verbose_name='Отчество', blank=True, max_length=256, null=True),
        ),
    ]
