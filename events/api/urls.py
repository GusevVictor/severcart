
from django.conf.urls import include, url
from events.api.views import show_event_page

urlpatterns = [
    url('^show_event_page/', show_event_page, name='show_event_page' ),
]
