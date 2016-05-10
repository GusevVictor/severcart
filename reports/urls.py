# -*- coding:utf-8 -*-

from django.conf.urls import url, include
from .views import (main_summary, 
                    amortizing, 
                    users, 
                    products, 
                    spent_money,)

urlpatterns = [
    url(r'^$', main_summary, name='main_summary'),
    url(r'^amortizing/', amortizing, name='amortizing'),
    url(r'^users/', users, name='users'),
    url(r'^products/',  products, name='products'),
    url(r'^spent_money/',  spent_money, name='spent_money'),
    url(r'^api/', include('reports.api.urls')),
]
