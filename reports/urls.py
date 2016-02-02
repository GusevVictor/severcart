from django.conf.urls import url, include
from .views import main_summary

urlpatterns = [
    url(r'^$', main_summary, name='main_summary'),
    #url(r'^api/', include('events.api.urls')),
]
