from django.conf.urls import url, include
from .views import service, delivery
from .views import handbook, edit_name
from .cbv import NamesView

urlpatterns = [
    url(r'^service/', service, name='service'),
    url(r'^delivery/', delivery, name='delivery' ),
    url(r'^$', handbook.as_view(), name='handbook'),
    url(r'^view_names/', NamesView.as_view(), name='view_names'),
    url(r'^edit_name/', edit_name, name='edit_name'),
    url(r'^api/', include('docs.api.urls')),
]
