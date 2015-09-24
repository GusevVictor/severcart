# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0004_auto_20150920_2110'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('city_name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='FirmTonerRefill',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('firm_name', models.CharField(max_length=256)),
                ('firm_contacts', models.TextField()),
                ('firm_address', models.TextField()),
                ('firm_comments', models.TextField()),
                ('firm_city', models.ForeignKey(to='index.City')),
            ],
        ),
        migrations.RemoveField(
            model_name='cartridgeitem',
            name='cart_code',
        ),
    ]
