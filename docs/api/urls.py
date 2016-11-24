from django.conf.urls import url, include
from .views import (del_cart_name,
                    del_city,
                    generate_act, 
                    generate_csv, 
                    generate_pdf,
                    calculate_sum,
                    generate_return_act,
                    clear_bufer,
                    )

urlpatterns = [
    url(r'^del_cart_name/', del_cart_name, name='del_cart_name'),
    url(r'^del_city/', del_city, name='del_city'),
    url(r'^generate_act/',  generate_act,  name='generate_act'),
    url(r'^generate_csv/',  generate_csv,  name='generate_csv'),
    url(r'^generate_pdf/',  generate_pdf,  name='generate_pdf'),
    url(r'^calculate_sum/', calculate_sum, name='calculate_sum'),
    url(r'^generate_return_act/', generate_return_act, name='generate_return_act'),
    url(r'^clear_bufer/', clear_bufer, name='clear_bufer'),
]
