
from django.conf.urls import include, url
from service.api.views import send_test_email, settings_email

urlpatterns = [
    url('^send_test_email/', send_test_email, name='send_test_email' ),
    url('^settings_email/', settings_email, name='settings_email' ),
]
