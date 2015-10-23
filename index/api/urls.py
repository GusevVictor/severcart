
from django.conf.urls import include, url

urlpatterns = [
#    url(r'^admin/', include(admin.site.urls)),
    url('^city_list/', 'index.api.views.city_list'),
	url('^inx/', 'index.api.views.inx'),
]
