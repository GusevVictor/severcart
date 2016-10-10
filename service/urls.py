# -*- coding:utf-8 -*-

from django.conf.urls import url, include
from .views import submenu, settings_mail, general_settings

urlpatterns = [
    url(r'^$', submenu, name='submenu'),
    url(r'settings_mail/', settings_mail, name='settings_mail'),
    url(r'general_settings/', general_settings, name='general_settings'),
    url(r'^api/', include('service.api.urls')),
]
