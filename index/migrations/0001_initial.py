# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-17 18:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CartridgeItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cart_number', models.IntegerField(db_index=True, null=True)),
                ('cart_number_prefix', models.CharField(max_length=256, null=True)),
                ('cart_number_postfix', models.CharField(max_length=256, null=True)),
                ('cart_date_added', models.DateField(db_index=True)),
                ('cart_date_change', models.DateField(db_index=True)),
                ('cart_status', models.IntegerField(choices=[(1, 'Full and in stock'), (2, 'In use'), (3, 'Empty and in stock'), (4, 'On restoration'), (5, 'Full and in basket'), (6, 'Empty and in basket')], default=1)),
                ('cart_number_refills', models.IntegerField(db_index=True, default=0)),
                ('comment', models.TextField(blank=True, verbose_name='Comment')),
                ('delivery_doc', models.IntegerField(db_index=True, default=0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CartridgeItemName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cart_itm_name', models.CharField(max_length=256)),
                ('comment', models.TextField(blank=True, verbose_name='Comment')),
            ],
        ),
        migrations.CreateModel(
            name='CartridgeType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cart_type', models.CharField(max_length=256, verbose_name='The name of the new type')),
                ('comment', models.TextField(blank=True, verbose_name='Comment')),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city_name', models.CharField(max_length=256, verbose_name='Enter the name of the city')),
            ],
        ),
        migrations.CreateModel(
            name='FirmTonerRefill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firm_name', models.CharField(max_length=256, verbose_name='Name')),
                ('firm_contacts', models.TextField(null=True, verbose_name='Contacts')),
                ('firm_address', models.TextField(null=True, verbose_name='Address')),
                ('firm_comments', models.TextField(null=True, verbose_name='Comment')),
                ('firm_city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.City', verbose_name='Select city')),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationUnits',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='index.OrganizationUnits')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('_default_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='cartridgeitemname',
            name='cart_itm_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.CartridgeType'),
        ),
        migrations.AddField(
            model_name='cartridgeitem',
            name='cart_itm_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.CartridgeItemName'),
        ),
        migrations.AddField(
            model_name='cartridgeitem',
            name='departament',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='index.OrganizationUnits'),
        ),
        migrations.AddField(
            model_name='cartridgeitem',
            name='filled_firm',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='index.FirmTonerRefill'),
        ),
    ]
