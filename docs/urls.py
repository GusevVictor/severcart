from django.conf.urls import url, include
from .views import service, delivery
from .views import handbook, edit_name, ViewSendActs
from .cbv import NamesView, TypesView

urlpatterns = [
    url(r'^service/', service, name='service'),
    url(r'^delivery/', delivery, name='delivery' ),
    url(r'^$', handbook.as_view(), name='handbook'),
    url(r'^view_names/', NamesView.as_view(), name='view_names'),
    url(r'^view_types/', TypesView.as_view(), name='view_types'),
    url(r'^edit_name/', edit_name, name='edit_name'),
    url(r'^view_send_acts/', ViewSendActs.as_view(), name='view_send_acts'),
    url(r'^api/', include('docs.api.urls')),
]
