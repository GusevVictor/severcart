# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('index', '0006_auto_20150926_2056'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnconUser',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('department', models.ForeignKey(to='index.Category', blank=True, null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='firmtonerrefill',
            name='firm_city',
            field=models.ForeignKey(to='index.City', blank=True, verbose_name='Выберите город'),
        ),
    ]
