"""
WSGI config for newskald_ru project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os, sys, site


site.addsitedir('C:/work/OpenServer/venv/Lib/site-packages/')

# Add the app's directory to the PYTHONPATH

sys.path.append('C:/work/OpenServer/ancon/')
sys.path.append('C:/work/OpenServer/ancon/newskald_ru/')
sys.path.append('C:/work/OpenServer/venv/Scripts/')

# Activate your virtual env
activate_env=os.path.expanduser('C:/work/OpenServer/venv/Scripts/activate_this.py')
with open(activate_env) as f:
    code = compile(f.read(), activate_env, 'exec')
    exec(code, dict(__file__=activate_env))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newskald_ru.settings-prod')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
