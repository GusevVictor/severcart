
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import TemplateView


urlpatterns = [
    url('', include('index.urls')),
    url(r'^manage_users/', include('accounts.urls', namespace='auth', app_name='accounts')),
    url(r'^api/', include('index.api.urls')),
    url(r'^events/', include('events.urls')),
    url(r'^docs/', include('docs.urls', namespace='docs')),
    url(r'^reports/', include('reports.urls', namespace='reports')),
    url(r'^service/', include('service.urls', namespace='service')),
] 

#if not settings.DEBUG:
#    urlpatterns = urlpatterns + static(settings.STATIC_ROOT, document_root=settings.STATIC_ROOT)
#    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#if settings.DEBUG == True:
#    urlpatterns += staticfiles_urlpatterns()

handler404 = 'index.views.handler404'
handler500 = 'index.views.handler500'
