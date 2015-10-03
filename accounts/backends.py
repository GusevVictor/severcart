from django.conf import settings
from django.contrib.auth.models import check_password
from accounts.models import AnconUser


class UserAuthBackend(object):
    """
    A custom authentication backend. Allows users to log in using their email address.
    """

    def authenticate(self, username=None, password=None):
        """
        Authentication method
        """
        try:
            user = AnconUser.objects.get(username=username)
            if user.check_password(password):
                return user
        except AnconUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            user = AnconUser.objects.get(pk=user_id)
            if user.is_active:
                return user
            return None
        except AnconUser.DoesNotExist:
            return None
