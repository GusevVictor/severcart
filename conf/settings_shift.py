# -*- coding:utf-8 -*-

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
DJ_PROJECT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(DJ_PROJECT_DIR)
WSGI_DIR = os.path.dirname(BASE_DIR)
REPO_DIR = os.path.dirname(WSGI_DIR)
DATA_DIR = os.environ.get('OPENSHIFT_DATA_DIR', BASE_DIR)



import sys
sys.path.append(os.path.join(REPO_DIR, 'libs'))
import secrets
SECRETS = secrets.getter(os.path.join(DATA_DIR, 'secrets.json'))

SECRET_KEY = SECRETS['secret_key']

from socket import gethostname
ALLOWED_HOSTS = [
    gethostname(), # For internal OpenShift load balancer security purposes.
    os.environ.get('OPENSHIFT_APP_DNS'), # Dynamically map to the OpenShift gear name.
    #'example.com', # First DNS alias (set up in the app)
    #'www.example.com', # Second DNS alias (set up in the app)
]

try:
    # очищаем кэш при перезагрузке сервера
    from django.core.cache import cache
    cache.clear()
except:
    pass

DEBUG = False
DEMO  = True


WSGI_APPLICATION = 'conf.wsgi_shift.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('OPENSHIFT_GEAR_NAME'),
        'USER': os.getenv('OPENSHIFT_POSTGRESQL_DB_USERNAME'),
        'PASSWORD': os.getenv('OPENSHIFT_POSTGRESQL_DB_PASSWORD'),
        'HOST': os.getenv('OPENSHIFT_POSTGRESQL_DB_HOST'),
        'PORT': os.getenv('OPENSHIFT_POSTGRESQL_DB_PORT'),
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(WSGI_DIR, 'static')

STATIC_ROOT_CSV = os.path.join(WSGI_DIR, 'static', 'csv')
MAX_COUNT_CSV_FILES = 20

STATIC_ROOT_DOCX = os.path.join(WSGI_DIR, 'static', 'docx')
MAX_COUNT_DOCX_FILES = 20

STATIC_ROOT_PDF = os.path.join(WSGI_DIR, 'static', 'pdf')
MAX_COUNT_PDF_FILES = 20

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
