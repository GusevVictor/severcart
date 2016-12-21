# -*- coding:utf-8 -*-

from django.conf.urls import url
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page
from django.conf import settings


if settings.DEBUG:
    # в режиме разработки кэширование отключаем
    urlpatterns = [
        url(r'^logic.js', TemplateView.as_view(template_name="dhtml/logic.html")),
        url(r'^common.js', TemplateView.as_view(template_name="dhtml/common.html")),
        url(r'^validate_money.js', TemplateView.as_view(template_name="dhtml/validate_money.html")),
        url(r'^add_session_items.js', TemplateView.as_view(template_name="dhtml/add_session_items.html")),
    ]
else:
    timeout = 60*60
    urlpatterns = [
        url(r'^logic.js', cache_page(timeout, key_prefix="logic")(TemplateView.as_view(template_name="dhtml/logic.html"))),
        url(r'^common.js', cache_page(timeout, key_prefix="common")(TemplateView.as_view(template_name="dhtml/common.html"))),
        url(r'^validate_money.js', cache_page(timeout, key_prefix="money")(TemplateView.as_view(template_name="dhtml/validate_money.html"))),
        url(r'^add_session_items.js', cache_page(timeout, key_prefix="add_session")(TemplateView.as_view(template_name="dhtml/add_session_items.html"))),
    ]
