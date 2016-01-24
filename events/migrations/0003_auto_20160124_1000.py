# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20160122_2314'),
    ]

    operations = [
        migrations.AddField(
            model_name='events',
            name='cart_action',
            field=models.IntegerField(null=True, max_length=5),
        ),
        migrations.AlterField(
            model_name='events',
            name='event_type',
            field=models.CharField(max_length=32, choices=[('AD', 'Добавление нового расходника'), ('TR', 'Передача расходника в пользование'), ('TF', 'Передача расходника на заправку'), ('RS', 'Возврат восстановленного картриджа на склад'), ('TB', 'Перемещение в корзину'), ('DC', 'Списание расходника'), ('TS', 'Передача пустого расходника на склад'), ('CU', 'Создание нового пользователя'), ('DU', 'Удаление пользователя')]),
        ),
    ]
