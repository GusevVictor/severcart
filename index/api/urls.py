
from django.conf.urls import include, url

urlpatterns = [
    url('^city_list/', 'index.api.views.city_list'),
	url('^inx/', 'index.api.views.inx'),
	url('^upd_dashboard_tbl/', 'index.api.views.upd_dashboard_tbl'),
]
