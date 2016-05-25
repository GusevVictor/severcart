# -*- coding:utf-8 -*-

from django.conf.urls import include, url
from index.views import robots_txt, favicon_ico

urlpatterns = [
    url('', include('index.urls', namespace='index')),
    url(r'^events/', include('events.urls', namespace='events')),
    url(r'^docs/', include('docs.urls', namespace='docs')),
    url(r'^reports/', include('reports.urls', namespace='reports')),
    url(r'^service/', include('service.urls', namespace='service')),
    url(r'^manage_users/', include('accounts.urls', namespace='auth')),
    url(r'^search/', include('search.urls', namespace='find')),
    url(r'^storages/', include('storages.urls', namespace='storages')),
    url(r'^dhtml/', include('dhtml.urls', namespace='dhtml')),
    url(r'^robots\.txt', robots_txt),
    url(r'^favicon\.ico', favicon_ico),
]
