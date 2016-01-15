# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Events',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('date_time', models.DateTimeField()),
                ('cart_number', models.IntegerField()),
                ('cart_type', models.CharField(max_length=256, null=True)),
                ('event_type', models.CharField(max_length=32, choices=[('AD', 'Добавление нового расходника'), ('TR', 'Передача расходника в пользование'), ('TF', 'Передача расходника на заправку'), ('RS', 'Возврат заправленного расходника на склад'), ('TB', 'Перемещение в корзину'), ('DC', 'Утилизация'), ('TS', 'Передача пустого расходника на склад'), ('CU', 'Создание нового пользователя'), ('DU', 'Удаление пользователя')])),
                ('event_user', models.CharField(max_length=64)),
                ('event_org', models.CharField(max_length=256, null=True)),
                ('event_firm', models.CharField(max_length=256, null=True)),
                ('departament', models.IntegerField()),
            ],
        ),
    ]
