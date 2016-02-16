
from django.conf.urls import include, url
from index.api.views import (   ajax_add_session_items, 
                                city_list,
                                del_node, 
                                turf_cartridge,
                                clear_session,
                                transfer_to_stock,
                                del_firm,
                            )
from accounts.api.views import del_users

urlpatterns = [
    url('^city_list/', city_list),
    url('^del_node/', del_node),
    url('^turf_cartridge/', turf_cartridge),
    url('^del_users/', del_users),
    url('^ajax_add_session_items/', ajax_add_session_items),
    url('^clear_session/', clear_session),
    url('^transfer_to_stock/', transfer_to_stock),
    url('^del_firm/', del_firm),
]
