
from django.conf.urls import include, url
from index.api.views import (   ajax_add_session_items, 
                                city_list,
                                del_node,
                                names_suggests, 
                                turf_cartridge,
                                clear_session,
                                transfer_to_stock,
                                del_firm,
                                transfer_to_basket,
                                get_cart_ou,
                                move_to_use,
                                view_events,
                                transfer_to_firm,
                                from_basket_to_stock,
                            )
from accounts.api.views import del_users

urlpatterns = [
    url('^city_list/', city_list, name='city_list'),
    url('^del_node/', del_node, name='del_node'),
    url('^turf_cartridge/', turf_cartridge, name='turf_cartridge'),
    url('^del_users/', del_users, name='del_users'),
    url('^ajax_add_session_items/', ajax_add_session_items, name='ajax_add_session_items'),
    url('^clear_session/', clear_session, name='clear_session'),
    url('^transfer_to_stock/', transfer_to_stock, name='transfer_to_stock'),
    url('^transfer_to_basket/', transfer_to_basket, name='transfer_to_basket'),
    url('^del_firm/', del_firm, name='del_firm'),
    url('^names_suggests/', names_suggests, name='names_suggests'),
    url('^get_cart_ou/', get_cart_ou, name='get_cart_ou'),
    url('^move_to_use/', move_to_use, name='move_to_use'),
    url('^view_events/', view_events, name='view_events'),
    url('^transfer_to_firm/', transfer_to_firm, name='api_transfer_to_firm'),
    url('^from_basket_to_stock/', from_basket_to_stock, name='from_basket_to_stock'),
]
