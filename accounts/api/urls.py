from django.conf.urls import url

from .views import send_repair_email, org_suggests

urlpatterns = [
    url(r'^send_repair_email/', send_repair_email, name='send_repair_email'),
    url(r'^org_suggests/', org_suggests, name='org_suggests'),
]
