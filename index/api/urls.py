
from django.conf.urls import include, url

urlpatterns = [
    url('^city_list/', 'index.api.views.city_list'),
	url('^inx/', 'index.api.views.inx'),
	url('^upd_dashboard_tbl/', 'index.api.views.upd_dashboard_tbl'),
	url('^del_node/', 'index.api.views.del_node'),
	url('^del_users/', 'accounts.api.views.del_users')
]
