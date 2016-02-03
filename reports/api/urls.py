from django.conf.urls import url, include
from .views import ajax_report

urlpatterns = [
    url(r'^$', ajax_report, name='ajax_report'),
]
