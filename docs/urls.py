from django.conf.urls import url, include
from .views import (handbook, 
                    delivery, 
                    edit_name, 
                    ViewSendActs, 
                    add_city,
                    edit_city,
                    ViewReturnActs,
                    )
from .cbv import NamesView, TypesView, CitiesView

urlpatterns = [
#    url(r'^service/', service, name='service'),
    url(r'^delivery/', delivery, name='delivery' ),
    url(r'^$', handbook.as_view(), name='handbook'),
    url(r'^view_names/', NamesView.as_view(), name='view_names'),
    url(r'^view_types/', TypesView.as_view(), name='view_types'),
    url(r'^edit_name/', edit_name, name='edit_name'),
    url(r'^cities/', CitiesView.as_view(), name='cities'),
    url(r'^add_city/', add_city, name='add_city'),
    url(r'^edit_city/', edit_city, name='edit_city'),
    url(r'^view_send_acts/', ViewSendActs.as_view(), name='view_send_acts'),
    url(r'^view_return_acts/', ViewReturnActs.as_view(), name='view_return_acts'),
    url(r'^api/', include('docs.api.urls')),
]
