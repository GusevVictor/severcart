
from django.conf.urls import include, url
from service.api.views import send_test_email

urlpatterns = [
    url('^send_test_email/', send_test_email, name='send_test_email' ),
]
