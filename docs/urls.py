from django.conf.urls import url, include
from .views import service, delivery
from .views import handbook

urlpatterns = [
    url(r'^service/', service, name='service'),
    url(r'^delivery/', delivery, name='delivery' ),
    url(r'^$', handbook.as_view(), name='handbook'),
]
