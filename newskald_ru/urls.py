
from django.conf.urls import include, url
from django.views.generic.base import TemplateView

urlpatterns = [
    url('', include('index.urls')),
    url(r'^manage_users/', include('accounts.urls', namespace='auth', app_name='accounts')),
    url(r'^api/', include('index.api.urls')),
    url(r'^events/', include('events.urls')),
    url(r'^docs/', include('docs.urls', namespace='docs')),
]

handler404 = 'index.views.handler404'
handler500 = 'index.views.handler500'
