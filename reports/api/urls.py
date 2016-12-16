from django.conf.urls import url
from .views import ajax_report, ajax_reports_users, ajax_firm, ajax_reports_brands, ajax_report_stale

urlpatterns = [
    url(r'^$', ajax_report, name='ajax_report'),
    url(r'^ajax_reports_users/', ajax_reports_users, name='ajax_reports_users'),
    url(r'^ajax_firm/', ajax_firm, name='ajax_firm'),
    url(r'^ajax_reports_brands/', ajax_reports_brands, name='ajax_reports_brands'),
    url(r'^ajax_report_stale/', ajax_report_stale, name='ajax_report_stale'),
]
