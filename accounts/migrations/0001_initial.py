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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(db_index=True, verbose_name='Логин', unique=True, max_length=64)),
                ('joined', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('first_name', models.CharField(blank=True, null=True, verbose_name='Имя', max_length=256)),
                ('last_name', models.CharField(blank=True, null=True, verbose_name='Фамилие', max_length=256)),
                ('patronymic', models.CharField(blank=True, null=True, verbose_name='Отчество', max_length=256)),
                ('department', models.ForeignKey(blank=True, to='index.OrganizationUnits', null=True, verbose_name='Организация')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
