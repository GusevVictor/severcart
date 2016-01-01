from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
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
            if not validate_password(password, user=user):
                return user
        except ValidationError:
            return None

    def get_user(self, user_id):
        try:
            user = AnconUser.objects.get(pk=user_id)
            if user.is_active:
                return user
            return None
        except AnconUser.DoesNotExist:
            return None
