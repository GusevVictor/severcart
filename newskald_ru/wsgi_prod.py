import os, sys, site

site.addsitedir('C:/venv/Lib/site-packages/')

# Add the app's directory to the PYTHONPATH
sys.path.append('C:/venv/Severcart/newskald_ru/')
sys.path.append('C:/venv/Severcart/')
sys.path.append('C:/venv/Scripts/')


# Activate your virtual env
activate_env=os.path.expanduser('C:/venv/Scripts/activate_this.py')
with open(activate_env) as f:
    code = compile(f.read(), activate_env, 'exec')
    exec(code, dict(__file__=activate_env))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newskald_ru.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
