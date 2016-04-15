from django.conf.urls import url

from .views import send_repair_email

urlpatterns = [
    url(r'^send_repair_email/', send_repair_email, name='send_repair_email'),
]
