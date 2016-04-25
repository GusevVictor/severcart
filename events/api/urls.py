
from django.conf.urls import include, url
from events.api.views import (
								show_event_page, 
								date_filter,
								view_cart_events,
							 )

urlpatterns = [
    url('^show_event_page/', show_event_page, name='show_event_page'),
    url('^date_filter/', date_filter, name='date_filter'),
    url('^view_cart_events/', view_cart_events, name='view_cart_events'),
]
