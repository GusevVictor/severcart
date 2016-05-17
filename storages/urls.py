from django.conf.urls import include, url
from storages.views import add_s, edit_s, ViewStorages

urlpatterns = [
    url(r'^$', ViewStorages.as_view(), name='all'),
    url(r'^add/', add_s, name='add'),
    url(r'^edit/', edit_s, name='edit'),
    url(r'^api/', include('storages.api.urls')),
]
