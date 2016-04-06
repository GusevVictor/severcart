# -*- coding:utf-8 -*-

from django.conf.urls import url, include
from .views import submenu, settings_mail

urlpatterns = [
    url(r'^$', submenu, name='submenu'),
    url(r'settings_mail/', settings_mail, name='settings_mail'),
]
