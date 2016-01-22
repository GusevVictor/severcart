# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='cart_number',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='events',
            name='event_type',
            field=models.CharField(max_length=32, choices=[('AD', 'Добавление нового расходника'), ('TR', 'Передача расходника в пользование'), ('TF', 'Передача расходника на заправку'), ('RS', 'Возврат заправленного расходника на склад'), ('TB', 'Перемещение в корзину'), ('DC', 'Списание расходника'), ('TS', 'Передача пустого расходника на склад'), ('CU', 'Создание нового пользователя'), ('DU', 'Удаление пользователя')]),
        ),
    ]
