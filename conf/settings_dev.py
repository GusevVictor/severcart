# -*- coding:utf-8 -*-

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DEMO = False

ALLOWED_HOSTS = ['*']


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^g$4c6-__#353*u_t9iovxd5g#)i$0o=bv5-ku+v=7#3ku*m%#'

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

WSGI_APPLICATION = 'conf.wsgi_dev.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'SKLAD6',
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

if DEBUG:
    STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
    MEDIAFILES_DIRS = (os.path.join(BASE_DIR, 'media'),)


STATIC_ROOT_CSV = os.path.join(BASE_DIR, 'static', 'csv')
MAX_COUNT_CSV_FILES = 20

STATIC_ROOT_DOCX = os.path.join(BASE_DIR, 'static', 'docx')
MAX_COUNT_DOCX_FILES = 20

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

if not DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



