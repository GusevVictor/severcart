
from django.conf.urls import include, url


urlpatterns = [
#    url(r'^admin/', include(admin.site.urls)),
    url('', include('index.urls')),
    url(r'^manage_users/', include('accounts.urls', namespace='auth', app_name='accounts')),
    url(r'^api/', include('index.api.urls')),
]
