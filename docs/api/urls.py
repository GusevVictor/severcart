from django.conf.urls import url, include
from .views import del_cart_name

urlpatterns = [
    url(r'^del_cart_name/', del_cart_name, name='del_cart_name'),

]
