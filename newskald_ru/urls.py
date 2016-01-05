
from django.conf.urls import include, url


urlpatterns = [
    url('', include('index.urls')),
    url(r'^manage_users/', include('accounts.urls', namespace='auth', app_name='accounts')),
    url(r'^api/', include('index.api.urls')),
    url(r'^events/', include('events.urls')),
]
