# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-11-22 10:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0008_auto_20161010_1116'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartridgeitem',
            name='bufer',
            field=models.BooleanField(default=False),
        ),
    ]
