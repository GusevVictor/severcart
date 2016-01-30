#!/usr/bin/env python
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newskald_ru.settings")

from accounts.models import AnconUser
user = AnconUser(username='root', is_admin = True)
user.set_password('root')
user.save()
