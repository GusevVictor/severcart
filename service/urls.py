# -*- coding:utf-8 -*-

from django.conf.urls import url, include
from .views import submenu

urlpatterns = [
    url(r'^$', submenu, name='submenu'),
]
