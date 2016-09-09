# -*- coding:utf-8 -*-

from django.conf.urls import url
from .views import search

urlpatterns = [
    url(r'^$', search, name='search'),
]
