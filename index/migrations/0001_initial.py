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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('cart_date_added', models.DateField()),
                ('cart_code', models.IntegerField()),
                ('cart_uses_count', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CartridgeItemName',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('cart_itm_name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='CartridgeOwner',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('owner', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='CartridgeType',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('cart_type', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('lft', models.PositiveIntegerField(db_index=True)),
                ('rgt', models.PositiveIntegerField(db_index=True)),
                ('tree_id', models.PositiveIntegerField(db_index=True)),
                ('depth', models.PositiveIntegerField(db_index=True)),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='cartridgeitemname',
            name='cart_itm_type',
            field=models.ForeignKey(to='index.CartridgeType'),
        ),
        migrations.AddField(
            model_name='cartridgeitem',
            name='cart_itm_name',
            field=models.ForeignKey(blank=True, null=True, to='index.CartridgeItemName'),
        ),
        migrations.AddField(
            model_name='cartridgeitem',
            name='cart_owner',
            field=models.ForeignKey(blank=True, null=True, to='index.CartridgeOwner'),
        ),
    ]
