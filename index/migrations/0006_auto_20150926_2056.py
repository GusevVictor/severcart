# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0005_auto_20150924_2122'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CartridgeOwner',
        ),
        migrations.AlterField(
            model_name='city',
            name='city_name',
            field=models.CharField(verbose_name='Введите название города', max_length=256),
        ),
        migrations.AlterField(
            model_name='firmtonerrefill',
            name='firm_address',
            field=models.TextField(blank=True, verbose_name='Адресс'),
        ),
        migrations.AlterField(
            model_name='firmtonerrefill',
            name='firm_city',
            field=models.ForeignKey(blank=True, to='index.City'),
        ),
        migrations.AlterField(
            model_name='firmtonerrefill',
            name='firm_comments',
            field=models.TextField(blank=True, verbose_name='Комментарии'),
        ),
        migrations.AlterField(
            model_name='firmtonerrefill',
            name='firm_contacts',
            field=models.TextField(blank=True, verbose_name='Контакты'),
        ),
        migrations.AlterField(
            model_name='firmtonerrefill',
            name='firm_name',
            field=models.CharField(verbose_name='Название', max_length=256),
        ),
    ]
