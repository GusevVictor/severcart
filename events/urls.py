from django.conf.urls import url, include
from events.views import show_events
from events.views import view_cartridge_events

urlpatterns = [
    url(r'^$', show_events, name='show_events'),
    url(r'^view_cartridge_events/', view_cartridge_events, name='view_cartridge_events'),
    url(r'^api/', include('events.api.urls')),
]
