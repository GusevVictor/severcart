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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('cart_date_added', models.DateField()),
                ('cart_filled', models.BooleanField()),
                ('cart_number_refills', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CartridgeItemName',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('cart_itm_name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='CartridgeType',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('cart_type', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('city_name', models.CharField(max_length=256, verbose_name='Введите название города')),
            ],
        ),
        migrations.CreateModel(
            name='FirmTonerRefill',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('firm_name', models.CharField(max_length=256, verbose_name='Название')),
                ('firm_contacts', models.TextField(blank=True, verbose_name='Контакты')),
                ('firm_address', models.TextField(blank=True, verbose_name='Адресс')),
                ('firm_comments', models.TextField(blank=True, verbose_name='Комментарии')),
                ('firm_city', models.ForeignKey(to='index.City', verbose_name='Выберите город', blank=True)),
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
            field=models.ForeignKey(to='index.CartridgeItemName'),
        ),
        migrations.AddField(
            model_name='cartridgeitem',
            name='cart_owner',
            field=models.ForeignKey(null=True, to='index.Category', blank=True),
        ),
    ]
