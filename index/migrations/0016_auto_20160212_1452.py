# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0015_auto_20160208_1620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='firmtonerrefill',
            name='firm_address',
            field=models.TextField(verbose_name='Адресс', null=True),
        ),
        migrations.AlterField(
            model_name='firmtonerrefill',
            name='firm_city',
            field=models.ForeignKey(verbose_name='Выберите город', to='index.City'),
        ),
        migrations.AlterField(
            model_name='firmtonerrefill',
            name='firm_comments',
            field=models.TextField(verbose_name='Комментарии', null=True),
        ),
        migrations.AlterField(
            model_name='firmtonerrefill',
            name='firm_contacts',
            field=models.TextField(verbose_name='Контакты', null=True),
        ),
    ]
