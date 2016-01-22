# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0008_auto_20160115_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartridgeitem',
            name='cart_date_change',
            field=models.DateField(default=datetime.datetime(2016, 1, 22, 18, 14, 8, 756835, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
