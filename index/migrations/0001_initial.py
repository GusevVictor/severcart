# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CartridgeItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('cart_name', models.CharField(max_length=256)),
                ('cart_date_added', models.DateField()),
                ('cart_code', models.IntegerField()),
                ('cart_uses_count', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CartridgeOwner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('owner', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='CartridgeType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('cart_type', models.CharField(max_length=256)),
            ],
        ),
        migrations.AddField(
            model_name='cartridgeitem',
            name='cart_owner',
            field=models.ForeignKey(to='index.CartridgeOwner'),
        ),
        migrations.AddField(
            model_name='cartridgeitem',
            name='cart_type',
            field=models.ForeignKey(to='index.CartridgeType'),
        ),
    ]
