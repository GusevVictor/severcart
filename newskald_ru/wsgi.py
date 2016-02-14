"""
WSGI config for Severcard project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newskald_ru.settings')

application = get_wsgi_application()

if not settings.DEBUG:
    from whitenoise.django import DjangoWhiteNoise
    application = DjangoWhiteNoise(application)
