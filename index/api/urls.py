
from django.conf.urls import include, url
from index.api.views import (	ajax_add_cart_items, 
								city_list, inx, 
								del_node, 
								turf_cartridge
							)
from accounts.api.views import del_users

urlpatterns = [
    url('^city_list/', city_list),
	url('^inx/', inx),
	url('^del_node/', del_node),
	url('^turf_cartridge/', turf_cartridge),
	url('^del_users/', del_users),
	url('^ajax_add_cart_items/', ajax_add_cart_items),

]
