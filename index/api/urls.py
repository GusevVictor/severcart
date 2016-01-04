
from django.conf.urls import include, url
from index.api.views import city_list
from index.api.views import inx
from index.api.views import upd_dashboard_tbl
from index.api.views import del_node
from index.api.views import turf_cartridge
from accounts.api.views import del_users

urlpatterns = [
    url('^city_list/', city_list),
	url('^inx/', inx),
	url('^upd_dashboard_tbl/', upd_dashboard_tbl),
	url('^del_node/', del_node),
	url('^turf_cartridge/', turf_cartridge),
	url('^del_users/', del_users)
]
