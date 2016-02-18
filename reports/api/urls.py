from django.conf.urls import url, include
from .views import ajax_report, ajax_reports_users

urlpatterns = [
    url(r'^$', ajax_report, name='ajax_report'),
    url(r'^ajax_reports_users/', ajax_reports_users, name='ajax_reports_users'),
]
