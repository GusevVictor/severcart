#!/usr/bin/env python
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newskald_ru.settings")

from accounts.models import AnconUser
user = AnconUser(username='Admin', is_admin = True)
p1 = input('Enter password: ')
p2 = input('Enter password again: ')

if p1 == p2:
	user.set_password('root')
	user.save()
else:
	print('User not created. Passwords not equal.')
