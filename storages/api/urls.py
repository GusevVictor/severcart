from django.conf.urls import url, include
from .views import del_s, set_default

urlpatterns = [
    url(r'^set_default/', set_default, name='set_default'),
    url(r'del_s', del_s, name='del_s'),
]
