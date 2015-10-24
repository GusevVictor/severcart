# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Events',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('event_type', models.IntegerField(choices=[(1, 'Добавление нового расходника'), (2, 'Передача расходника в пользование'), (3, 'Передача расходники на заправку'), (4, 'Утилизация'), (5, 'Передача пустого расходника на склад'), (6, 'Создание нового пользователя'), (7, 'Удаление пользователя')])),
                ('date_time', models.DateTimeField()),
                ('comment', models.CharField(max_length=256)),
                ('cart_itm', models.ForeignKey(to='index.CartridgeItem', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Summary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('full_on_stock', models.IntegerField()),
                ('empty_on_stock', models.IntegerField()),
                ('empty', models.IntegerField()),
                ('filles', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='cartridgetype',
            name='cart_type',
            field=models.CharField(verbose_name='Название нового типа', max_length=256),
        ),
    ]
