# -*- coding:utf-8 -*-

from django.conf.urls import url, include
from .views import search

urlpatterns = [
    url(r'^$', search, name='search'),
]
