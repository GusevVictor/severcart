from django.conf.urls import url, include
from .views import del_cart_name, generate_act, generate_csv, generate_pdf

urlpatterns = [
    url(r'^del_cart_name/', del_cart_name, name='del_cart_name'),
    url(r'^generate_act/', generate_act, name='generate_act'),
    url(r'^generate_csv/', generate_csv, name='generate_csv'),
    url(r'^generate_pdf/', generate_pdf, name='generate_pdf'),

]
