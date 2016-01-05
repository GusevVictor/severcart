from django.conf.urls import url
from events.views import show_events

urlpatterns = [
    url(r'^$', show_events, name='show_events'),
]
