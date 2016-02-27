# -*- coding:utf-8 -*-

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

DEMO  = True

ALLOWED_HOSTS = ['*']


SECRET_KEY = os.getenv('OPENSHIFT_SECRET_TOKEN')
# Application definition

INSTALLED_APPS = (
#    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'index',
    'mptt',
    'accounts',
    'events',
    'docs',
    'reports',
    'service',
)

WSGI_APPLICATION = 'newskald_ru.wsgi_shift.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'py',
        'USER': os.getenv('OPENSHIFT_POSTGRESQL_DB_USERNAME'),
        'PASSWORD': os.getenv('OPENSHIFT_POSTGRESQL_DB_PASSWORD'),
        'HOST': os.getenv('OPENSHIFT_POSTGRESQL_DB_HOST'),
        'PORT': os.getenv('OPENSHIFT_POSTGRESQL_DB_PORT'),
    }
}

if DEBUG:
    STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
    MEDIAFILES_DIRS = (os.path.join(BASE_DIR, 'media'),)


STATIC_ROOT_CSV = os.path.join(BASE_DIR, 'static', 'csv')
MAX_COUNT_CSV_FILES = 20

STATIC_ROOT_DOCX = os.path.join(BASE_DIR, 'static', 'docx')
MAX_COUNT_DOCX_FILES = 20

# for collect static utility
STATIC_ROOT = os.path.join(os.getenv('OPENSHIFT_REPO_DIR'), 'wsgi' ,'static')

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
