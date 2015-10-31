# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CartridgeItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('cart_date_added', models.DateField()),
                ('cart_filled', models.BooleanField()),
                ('cart_number_refills', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='CartridgeItemName',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('cart_itm_name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='CartridgeType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('cart_type', models.CharField(verbose_name='Название нового типа', max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('city_name', models.CharField(verbose_name='Введите название города', max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Events',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('event_type', models.IntegerField(choices=[(1, 'Добавление нового расходника'), (2, 'Передача расходника в пользование'), (3, 'Передача расходники на заправку'), (4, 'Утилизация'), (5, 'Передача пустого расходника на склад'), (6, 'Создание нового пользователя'), (7, 'Удаление пользователя')])),
                ('date_time', models.DateTimeField()),
                ('comment', models.CharField(max_length=256)),
                ('cart_itm', models.ForeignKey(to='index.CartridgeItem', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FirmTonerRefill',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('firm_name', models.CharField(verbose_name='Название', max_length=256)),
                ('firm_contacts', models.TextField(blank=True, verbose_name='Контакты')),
                ('firm_address', models.TextField(blank=True, verbose_name='Адресс')),
                ('firm_comments', models.TextField(blank=True, verbose_name='Комментарии')),
                ('firm_city', models.ForeignKey(blank=True, to='index.City', verbose_name='Выберите город')),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationUnits',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=254)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, related_name='children', to='index.OrganizationUnits', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Summary',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('full_on_stock', models.IntegerField(default=0)),
                ('empty_on_stock', models.IntegerField(default=0)),
                ('uses', models.IntegerField(default=0)),
                ('filled', models.IntegerField(default=0)),
                ('recycler_bin', models.IntegerField(default=0)),
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
            field=models.ForeignKey(blank=True, to='index.OrganizationUnits', null=True),
        ),
        migrations.AddField(
            model_name='cartridgeitem',
            name='filled_firm',
            field=models.ForeignKey(to='index.FirmTonerRefill', null=True),
        ),
    ]
