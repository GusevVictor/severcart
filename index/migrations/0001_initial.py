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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('cart_date_added', models.DateField(null=True, blank=True)),
                ('cart_filled', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='CartridgeItemName',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('cart_itm_name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='CartridgeType',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('cart_type', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
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
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('city_name', models.CharField(verbose_name='Введите название города', max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='FirmTonerRefill',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('firm_name', models.CharField(verbose_name='Название', max_length=256)),
                ('firm_contacts', models.TextField(verbose_name='Контакты', blank=True)),
                ('firm_address', models.TextField(verbose_name='Адресс', blank=True)),
                ('firm_comments', models.TextField(verbose_name='Комментарии', blank=True)),
                ('firm_city', models.ForeignKey(verbose_name='Выберите город', to='index.City', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='cartridgeitemname',
            name='cart_itm_type',
            field=models.ForeignKey(to='index.CartridgeType'),
        ),
        migrations.AddField(
            model_name='cartridgeitem',
            name='cart_itm_name',
            field=models.ForeignKey(to='index.CartridgeItemName', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='cartridgeitem',
            name='cart_owner',
            field=models.ForeignKey(to='index.Category', null=True, blank=True),
        ),
    ]
