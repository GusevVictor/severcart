"""newskald_ru URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url('^$', 'index.views.index'),
    url(r'^add_name/', 'index.views.add_cartridge_name'),
    url(r'^add_items/', 'index.views.add_cartridge_item'),
    url(r'^tree_list/', 'index.views.tree_list'),
    url(r'^add_type/', 'index.views.add_type'),
    url(r'^transfe_for_use/', 'index.views.transfe_for_use')
]
