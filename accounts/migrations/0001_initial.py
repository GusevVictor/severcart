# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnconUser',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, blank=True, verbose_name='last login')),
                ('username', models.CharField(db_index=True, unique=True, max_length=64, verbose_name='Логин')),
                ('joined', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('first_name', models.CharField(null=True, blank=True, max_length=256, verbose_name='Имя')),
                ('last_name', models.CharField(null=True, blank=True, max_length=256, verbose_name='Фамилие')),
                ('patronymic', models.CharField(null=True, blank=True, max_length=256, verbose_name='Отчество')),
                ('department', models.ForeignKey(null=True, to='index.Category', verbose_name='Организация', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
