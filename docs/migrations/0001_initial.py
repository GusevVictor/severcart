# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0010_auto_20160128_1815'),
    ]

    operations = [
        migrations.CreateModel(
            name='SCDoc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(null=True, db_index=True)),
                ('date', models.DateField(db_index=True)),
                ('title', models.CharField(max_length=256)),
                ('short_cont', models.TextField(blank=True)),
                ('money', models.IntegerField(null=True, db_index=True)),
                ('doc_type', models.IntegerField(default=1, choices=[(1, 'Договор поставки'), (2, 'Договор обслуживания'), (3, 'Акт передачи'), (4, 'Акт списания'), (5, 'Акт списания')])),
                ('departament', models.ForeignKey(to='index.OrganizationUnits')),
                ('firm', models.ForeignKey(to='index.FirmTonerRefill', null=True)),
            ],
        ),
    ]
